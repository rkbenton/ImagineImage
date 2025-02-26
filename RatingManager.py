import os
import re
import random
import enum
import boto3

from S3Manager import S3Manager


# ----------------------------
# Helper Function
# ----------------------------
def update_filename_with_rating(filename: str, rating: float) -> str:
    """
    Given a filename (e.g. "20250219T171207_output_image.png") and a rating,
    insert or update the rating marker " r[n]" (with one decimal place) immediately before the file extension.
    """
    base, ext = os.path.splitext(filename)
    # Regular expression to match an existing rating marker: a space, then r[<digit>.<digit>]
    rating_pattern = re.compile(r'(.*?)(?:\s*r\[\d\.\d\])?$')
    match = rating_pattern.fullmatch(base)
    if not match:
        # In case the base is not as expected, just use it as-is
        new_base = base
    else:
        new_base = match.group(1)
    # Append new rating marker formatted to one decimal place
    new_filename = f"{new_base} r[{rating:.1f}]{ext}"
    return new_filename


def is_image_file(file_path: str) -> bool:
    """
    Returns True if the file_path points to an image file,
    determined by its file extension.
    """
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
    ext = os.path.splitext(file_path)[1].lower()
    return ext in image_extensions


# ----------------------------
# SortEnum for ordering
# ----------------------------
class SortEnum(enum.Enum):
    ASCENDING = 1
    DESCENDING = 2
    RANDOM = 3
    NONE = 4

# ----------------------------
# RatingManager class
# ----------------------------
class RatingManager:
    def __init__(self, s3_manager: S3Manager):
        self.s3_manager = s3_manager
        self.rating_list = []  # List of file paths (unrated files)
        self.current_index = 0

    def find_all_rated_files(self, dirpath: str, rating_range: tuple[float, float], sort: SortEnum) -> list[str]:
        """
        Scan the directory for files that have a rating marker in their name.
        Optionally, filter files to those whose rating is within rating_range.
        The returned list is sorted based on the sort parameter.
        """
        rated_files = []
        rating_pattern = re.compile(r' r\[(\d\.\d)\]')
        for filename in os.listdir(dirpath):
            full_path = os.path.join(dirpath, filename)
            if os.path.isfile(full_path):
                match = rating_pattern.search(filename)
                if match:
                    rating_value = float(match.group(1))
                    if rating_range[0] <= rating_value <= rating_range[1]:
                        rated_files.append(full_path)

        # Sorting as requested
        if sort == SortEnum.ASCENDING:
            rated_files.sort(key=lambda fp: float(rating_pattern.search(os.path.basename(fp)).group(1)))
        elif sort == SortEnum.DESCENDING:
            rated_files.sort(key=lambda fp: float(rating_pattern.search(os.path.basename(fp)).group(1)), reverse=True)
        elif sort == SortEnum.RANDOM:
            random.shuffle(rated_files)
        # If sort == SortEnum.NONE, leave unsorted
        return rated_files

    def find_all_unrated_files(self, dirpath: str) -> list[str]:
        """
        Scan the directory and return a list of file paths that do not have a rating marker in their filename.
        Only include files that are recognized as image files.
        """
        unrated_files = []
        rating_pattern = re.compile(r' r\[\d\.\d\]')
        for filename in os.listdir(dirpath):
            full_path = os.path.join(dirpath, filename)
            # Check if it is a file and an image file
            if os.path.isfile(full_path) and is_image_file(full_path):
                if not rating_pattern.search(filename):
                    unrated_files.append(full_path)
        return unrated_files

    def start_rating(self, directory_path: str) -> list[str]:
        """
        Initialize the rating session by creating a list of all unrated image files in the directory.
        This list is used to track progress during the file-rating process.
        """
        self.rating_list = self.find_all_unrated_files(directory_path)
        self.current_index = 0
        return self.rating_list

    def rate_file(self, file_path: str, rating: float):
        """
        Insert (or update) the rating marker in the file's name (and its companion files, if any).
        The new marker ' r[n]' (n formatted to one decimal place) is placed immediately before the file extension.
        After renaming the file(s) locally, the S3Manager is called to update the corresponding file(s) in S3.
        """
        print(f"Rating {file_path} as {rating:.1f}")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' does not exist.")
        if not (0.0 <= rating <= 5.0):
            raise ValueError("Rating must be between 0.0 and 5.0.")

        dir_path = os.path.dirname(file_path)      # e.g. 'image_out/creative'
        s3_prefix = os.path.basename(os.path.dirname(file_path)) # e.g. 'creative'

        original_filename = os.path.basename(file_path)
        if len(original_filename) < 15:
            raise ValueError("Filename does not contain the expected date-time prefix.")

        # Determine the common date-time prefix (first 15 characters)
        prefix = original_filename[:15]

        # Process all companion files (files that start with the same date-time prefix)
        for fname in os.listdir(dir_path):
            if fname.startswith(prefix):
                old_full_path = os.path.join(dir_path, fname)
                new_fname = update_filename_with_rating(fname, rating)
                new_full_path = os.path.join(dir_path, new_fname)
                # Only rename if needed
                if new_fname != fname:
                    os.rename(old_full_path, new_full_path)
                    # Update the file in S3: use the leaf_dir_name / filename (or key) as the identifier.
                    try:
                        if self.s3_manager.is_in_s3(s3_prefix, fname):
                            self.s3_manager.change_name_in_cloud(s3_prefix=s3_prefix, cur_filename=fname, new_filename=new_fname)
                        else:
                            print(f"File '{new_fname}' was not found in the S3 bucket. Uploading now.")
                            self.s3_manager.upload_to_s3(file_path=new_full_path, s3_key=f"{s3_prefix}/{new_fname}")
                    except Exception as e:
                        print(f"Warning: S3 update failed for '{fname}' -> '{new_fname}': {e}")

                    # If the rated file is in the rating list, update its entry with the new filename
                    if old_full_path in self.rating_list:
                        idx = self.rating_list.index(old_full_path)
                        self.rating_list[idx] = new_full_path

    def num_remaining_to_rate(self) -> int:
        """
        Return the number of files remaining in the rating list (from the current index onward).
        """
        return len(self.rating_list) - self.current_index

    def next(self) -> str:
        """
        Move to the next file in the rating list and return its file path.
        Raises an exception if already at the end of the list.
        """
        if self.current_index >= len(self.rating_list) - 1:
            raise IndexError("No more files to rate.")
        self.current_index += 1
        return self.rating_list[self.current_index]

    def prev(self) -> str:
        """
        Move to the previous file in the rating list and return its file path.
        Raises an exception if already at the beginning of the list.
        """
        if self.current_index <= 0:
            raise IndexError("Already at the first file.")
        self.current_index -= 1
        return self.rating_list[self.current_index]

# ----------------------------
# Example Usage
# ----------------------------
if __name__ == "__main__":
    # Initialize S3Manager and RatingManager
    s3_manager = S3Manager()
    rating_manager = RatingManager(s3_manager)

    # Suppose images are stored in the directory "images"
    directory = "images"

    # Start rating session for unrated files
    unrated_files = rating_manager.start_rating(directory)
    print("Unrated Files:", unrated_files)

    # Example: rate the first file in the list with a rating of 3.4
    if unrated_files:
        file_to_rate = unrated_files[rating_manager.current_index]
        print("Rating file:", file_to_rate)
        rating_manager.rate_file(file_to_rate, 3.4)
        print("Remaining files to rate:", rating_manager.num_remaining_to_rate())
