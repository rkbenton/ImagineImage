import os

import pytest

from RatingManager import (
    RatingManager,
    update_filename_with_rating,
    SortEnum,
    is_image_file  # assuming is_image_file is exported from RatingManager.py
)


# ----------------------------
# Dummy S3Manager for Testing
# ----------------------------
class DummyS3Manager:
    def __init__(self):
        self.changes = []  # Records tuples of (cur_key, new_key)

    def change_name_in_cloud(self, cur_key: str, new_key: str):
        # Instead of real S3 operations, simply record the change.
        self.changes.append((cur_key, new_key))


# ----------------------------
# Tests for is_image_file
# ----------------------------
def test_is_image_file_true(tmp_path):
    # Create a dummy image file path.
    image_path = tmp_path / "sample_image.JPG"
    # Even though the file doesn't need to exist for the extension check,
    # we can still test the function's behavior.
    assert is_image_file(str(image_path))


def test_is_image_file_false(tmp_path):
    # Non-image file with a .txt extension.
    non_image_path = tmp_path / "document.txt"
    assert not is_image_file(str(non_image_path))


# ----------------------------
# Tests for update_filename_with_rating
# ----------------------------
def test_update_filename_with_rating_no_existing_rating():
    original = "20250219T171207_output_image.png"
    rating = 3.4
    expected = "20250219T171207_output_image r[3.4].png"
    result = update_filename_with_rating(original, rating)
    assert result == expected


def test_update_filename_with_rating_existing_rating():
    original = "20250219T171207_output_image r[1.0].png"
    rating = 4.2
    expected = "20250219T171207_output_image r[4.2].png"
    result = update_filename_with_rating(original, rating)
    assert result == expected


# ----------------------------
# Tests for find_all_rated_files
# ----------------------------
def test_find_all_rated_files(tmp_path):
    # Create files: two with ratings, one unrated image file, one non-image file.
    file1 = tmp_path / "20250219T171207_img1 r[2.3].png"
    file1.write_text("dummy")
    file2 = tmp_path / "20250220T171207_img2 r[4.5].jpg"
    file2.write_text("dummy")
    file3 = tmp_path / "20250221T171207_img3.png"  # unrated image file
    file3.write_text("dummy")
    file4 = tmp_path / "20250222T171207_doc.txt"  # unrated non-image file
    file4.write_text("dummy")

    dummy_s3 = DummyS3Manager()
    rm = RatingManager(dummy_s3)

    # Test ascending sort on rated files (all rated files are images)
    rated_files = rm.find_all_rated_files(str(tmp_path), (0.0, 5.0), SortEnum.ASCENDING)
    expected_order = [str(file1), str(file2)]
    assert rated_files == expected_order

    # Test descending sort
    rated_files_desc = rm.find_all_rated_files(str(tmp_path), (0.0, 5.0), SortEnum.DESCENDING)
    expected_order_desc = [str(file2), str(file1)]
    assert rated_files_desc == expected_order_desc

    # Test random sort (order is not guaranteed but the set should match)
    rated_files_rand = rm.find_all_rated_files(str(tmp_path), (0.0, 5.0), SortEnum.RANDOM)
    assert set(rated_files_rand) == set(expected_order)


# ----------------------------
# Tests for find_all_unrated_files and start_rating
# ----------------------------
def test_find_all_unrated_files(tmp_path):
    # Create files: one unrated image, one rated image, one unrated text file.
    file1 = tmp_path / "20250219T171207_img1.png"  # image, unrated
    file1.write_text("dummy")
    file2 = tmp_path / "20250220T171207_img2 r[4.5].jpg"  # rated image
    file2.write_text("dummy")
    file3 = tmp_path / "20250221T171207_doc.txt"  # non-image, unrated
    file3.write_text("dummy")

    dummy_s3 = DummyS3Manager()
    rm = RatingManager(dummy_s3)

    unrated = rm.find_all_unrated_files(str(tmp_path))
    # Only file1 should be included because file3 is not an image file.
    expected = {str(file1)}
    assert set(unrated) == expected


def test_start_rating(tmp_path):
    file1 = tmp_path / "20250219T171207_img1.png"  # unrated image
    file1.write_text("dummy")
    file2 = tmp_path / "20250220T171207_img2 r[4.5].jpg"  # rated image
    file2.write_text("dummy")
    file3 = tmp_path / "20250221T171207_doc.txt"  # unrated non-image
    file3.write_text("dummy")

    dummy_s3 = DummyS3Manager()
    rm = RatingManager(dummy_s3)

    rating_list = rm.start_rating(str(tmp_path))
    # Only unrated image file should be in the rating list.
    expected = {str(file1)}
    assert set(rating_list) == expected
    assert rm.current_index == 0


# ----------------------------
# Tests for rate_file
# ----------------------------
def test_rate_file(tmp_path):
    # Create two companion files with the same date-time prefix.
    file_img = tmp_path / "20250219T171207_img1.png"
    file_img.write_text("image content")
    file_prompt = tmp_path / "20250219T171207_prompt.txt"
    file_prompt.write_text("prompt content")

    dummy_s3 = DummyS3Manager()
    rm = RatingManager(dummy_s3)
    # Manually add the image file to the rating list (only image files are rated)
    rm.rating_list = [str(file_img)]

    # Rate the file with a valid rating.
    rm.rate_file(str(file_img), 3.4)

    # Expected new filenames
    new_img_name = "20250219T171207_img1 r[3.4].png"
    new_prompt_name = "20250219T171207_prompt r[3.4].txt"
    new_img_path = tmp_path / new_img_name
    new_prompt_path = tmp_path / new_prompt_name

    # Verify that the new files exist and the old ones do not.
    assert new_img_path.exists()
    assert new_prompt_path.exists()
    assert not file_img.exists()
    assert not (tmp_path / "20250219T171207_prompt.txt").exists()

    # Verify that the dummy S3 manager recorded both file renamings.
    assert ("20250219T171207_img1.png", new_img_name) in dummy_s3.changes
    assert ("20250219T171207_prompt.txt", new_prompt_name) in dummy_s3.changes

    # Verify that the rating list was updated with the new file path.
    assert rm.rating_list[0] == str(new_img_path)

    # Test that a rating out of bounds raises a ValueError.
    with pytest.raises(ValueError):
        rm.rate_file(str(new_img_path), 6.0)

    # Test that rating a non-existent file raises a FileNotFoundError.
    with pytest.raises(FileNotFoundError):
        rm.rate_file(str(tmp_path / "non_existent_file.png"), 3.0)


# ----------------------------
# Tests for next() and prev() with only image files
# ----------------------------
def test_navigation_next_prev(tmp_path):
    # Create three unrated image files.
    file1 = tmp_path / "20250219T171207_img1.png"
    file1.write_text("dummy")
    file2 = tmp_path / "20250220T171207_img2.jpg"
    file2.write_text("dummy")
    file3 = tmp_path / "20250221T171207_img3.jpeg"
    file3.write_text("dummy")
    # Also create a non-image file to ensure it's excluded.
    file4 = tmp_path / "20250222T171207_doc.txt"
    file4.write_text("dummy")

    dummy_s3 = DummyS3Manager()
    rm = RatingManager(dummy_s3)

    # Start rating; this will populate the rating_list with only image files.
    rm.start_rating(str(tmp_path))

    # The rating_list should contain only the three image files.
    expected_files = {str(file1), str(file2), str(file3)}
    assert set(rm.rating_list) == expected_files

    # Verify initial file is one of the expected images.
    current_file = rm.rating_list[rm.current_index]
    assert current_file in expected_files

    # Move to the next file.
    next_file = rm.next()
    assert next_file in expected_files

    # Move to the next file again.
    next_file = rm.next()
    assert next_file in expected_files

    # Calling next() now should raise an IndexError (no more files).
    with pytest.raises(IndexError):
        rm.next()

    # Move back using prev().
    prev_file = rm.prev()
    assert prev_file in expected_files
    prev_file = rm.prev()
    assert prev_file in expected_files

    # Calling prev() now should raise an IndexError.
    with pytest.raises(IndexError):
        rm.prev()


def test_navigation_rating_with_companions(tmp_path):
    # Create three image files and three matching companion text files.
    file1_img = tmp_path / "20250219T171207_img1.png"
    file1_txt = tmp_path / "20250219T171207_prompt.txt"
    file1_img.write_text("img1 content")
    file1_txt.write_text("prompt1 content")

    file2_img = tmp_path / "20250220T171207_img2.png"
    file2_txt = tmp_path / "20250220T171207_prompt.txt"
    file2_img.write_text("img2 content")
    file2_txt.write_text("prompt2 content")

    file3_img = tmp_path / "20250221T171207_img3.png"
    file3_txt = tmp_path / "20250221T171207_prompt.txt"
    file3_img.write_text("img3 content")
    file3_txt.write_text("prompt3 content")

    # Initialize RatingManager with the dummy S3 manager.
    dummy_s3 = DummyS3Manager()
    rm = RatingManager(dummy_s3)

    # Start the rating session: only image files (unrated) are added.
    rm.start_rating(str(tmp_path))
    # Force an ascending order based on filename.
    rm.rating_list.sort()

    # Verify that the sorted rating_list is as expected.
    expected_order = [
        str(file1_img),
        str(file2_img),
        str(file3_img)
    ]
    assert rm.rating_list == expected_order

    # At this point, current_index is 0 (file1_img).
    # Call next() to skip the first file.
    file2_path = rm.next()  # Now current_index becomes 1.
    assert file2_path == str(file2_img)

    # Rate the second file (file2) with a rating of 2.0.
    rm.rate_file(file2_path, 2.0)
    # After rating, file2 and its companion should be updated.
    new_file2_img = tmp_path / "20250220T171207_img2 r[2.0].png"
    new_file2_txt = tmp_path / "20250220T171207_prompt r[2.0].txt"
    assert new_file2_img.exists()
    assert new_file2_txt.exists()

    # Call next() to move to the third file.
    file3_path = rm.next()  # Now current_index becomes 2.
    assert file3_path == str(file3_img)

    # Rate the third file (file3) with a rating of 3.0.
    rm.rate_file(file3_path, 3.0)
    new_file3_img = tmp_path / "20250221T171207_img3 r[3.0].png"
    new_file3_txt = tmp_path / "20250221T171207_prompt r[3.0].txt"
    assert new_file3_img.exists()
    assert new_file3_txt.exists()

    # Call prev() to go back to the second file.
    file2_back = rm.prev()  # Current index returns to 1.
    # Verify that file2's filename indicates a rating of 2.0.
    assert "r[2.0]" in os.path.basename(file2_back)

    # Now update the rating on file2 from 2.0 to 2.1.
    rm.rate_file(file2_back, 2.1)
    updated_file2_img = tmp_path / "20250220T171207_img2 r[2.1].png"
    updated_file2_txt = tmp_path / "20250220T171207_prompt r[2.1].txt"
    assert updated_file2_img.exists()
    assert updated_file2_txt.exists()

    # Call next() to move forward to file3.
    file3_forward = rm.next()  # Moves back to index 2.
    # Verify file3 still has its original rating of 3.0.
    assert "r[3.0]" in os.path.basename(file3_forward)

    # Call prev() to go back to file2 again.
    file2_prev = rm.prev()  # Should be at index 1 again.
    # Verify that the rating for file2 is now updated to 2.1.
    assert "r[2.1]" in os.path.basename(file2_prev)

    # Finally, verify that file1 (which was skipped and not rated) and its companion remain unrated.
    file1_txt_expected = tmp_path / "20250219T171207_prompt.txt"
    assert file1_txt_expected.exists()
    # And its image file should remain without a rating marker.
    assert "r[" not in os.path.basename(file1_img)
