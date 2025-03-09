import json
import os
import random
import time
from datetime import datetime
from typing import List, Dict, Tuple
import re

from S3Manager import S3Manager

import logging

from imim_utils import print_progress_bar

logger = logging.getLogger(__name__)


def list_local_files(root_dir):
    local_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, root_dir)
            local_files.append({
                'name': relative_path,
                'size': os.path.getsize(full_path),
                'last_modified': datetime.fromtimestamp(os.path.getmtime(full_path))
            })
    return local_files


def create_approximating_key(filename) -> str:
    """
    Given a filepath like 'halloween/20250218T160340_prompt.txt', this
    will return the minimally unique key of 'halloween/20250218T160340.txt'.
    In the event of oddball keys, it will simply return them, e.g. 'christmas/'.
    """
    path, filename = os.path.split(filename)
    date_time = filename[:15] if len(filename) > 15 else filename
    extension = os.path.splitext(filename)[1]
    return f"{path}/{date_time}{extension}"


def match_files(s3_files, local_files, match_mode='exact'):
    s3_set = set()
    local_set = set()

    for file in s3_files:
        if match_mode == 'exact':
            s3_set.add(file['name'])
        elif match_mode == 'approximate':
            path, filename = os.path.split(file['name'])
            date_time = filename[:15]
            extension = os.path.splitext(filename)[1]
            s3_set.add(f"{path}/{date_time}{extension}")

    for file in local_files:
        if match_mode == 'exact':
            local_set.add(file['name'])
        elif match_mode == 'approximate':
            path, filename = os.path.split(file['name'])
            date_time = filename[:15]
            extension = os.path.splitext(filename)[1]
            local_set.add(f"{path}/{date_time}{extension}")

    return s3_set, local_set


def perform_set_operations(s3_files, local_files, match_mode='exact'):
    s3_set, local_set = match_files(s3_files, local_files, match_mode)

    files_in_both = s3_set.intersection(local_set)
    files_only_local = local_set - s3_set
    files_only_s3 = s3_set - local_set

    return files_in_both, files_only_local, files_only_s3


def find_naming_mismatches(files_in_both_exact, files_in_both_approx):
    mismatches = files_in_both_approx - files_in_both_exact
    return mismatches


def enforce_str_len(key, length=40):
    # Truncate the key if it's longer than the specified length
    truncated_key = key[:length]
    # Pad the key with spaces to ensure it's exactly `length` characters
    padded_key = truncated_key.ljust(length)
    return padded_key


def copy_s3_files_to_local(copy_s3_to_local: list, s3_manager: S3Manager, save_directory_path="image_out",
                           max_to_copy=0, randomize=False,
                           theme_name_filter="") -> None:
    """
    Copies files from an S3 bucket to a local directory.

    :param copy_s3_to_local: List of dictionaries containing S3 file metadata, where each dictionary has a "name" key.
    :param s3_manager: utility for S3
    :param save_directory_path: root of where local images should go, default is "image_out"
    :param max_to_copy: Maximum number of files to copy (0 means copy all available files).
    :param randomize: If True, randomizes the order of files before copying.
    :param theme_name_filter: If provided, filters files to only those starting with this theme name.
    """
    num_files = len(copy_s3_to_local)

    # Apply theme filter if specified
    if num_files > 0 and theme_name_filter:
        filtered_list = [item for item in copy_s3_to_local if item["name"].startswith(theme_name_filter)]
        num_files = len(filtered_list)
    else:
        filtered_list = copy_s3_to_local

    if num_files == 0:
        print("No files need to be copied from S3")
        return

    num_copied = 0

    # Determine the number of files to copy; max_to_copy of zero means copy all
    max_to_copy = num_files if max_to_copy < 1 else min(max_to_copy, num_files)

    # Randomize if necessary
    if randomize:
        random.shuffle(filtered_list)

    print(f"Copying {max_to_copy} files down from S3")
    print_progress_bar(0, max_to_copy, prefix='Progress:', suffix='Complete', length=50)

    for count, s3_file in enumerate(filtered_list):
        file_key = s3_file['name']
        local_path = os.path.join(save_directory_path, file_key)
        s3_manager.download_from_s3(file_key, local_path)
        num_copied += 1
        print_progress_bar(count + 1, max_to_copy, prefix='Progress:', suffix='Complete', length=50)

        if num_copied >= max_to_copy:
            break


def upload_local_files_to_s3(copy_local_to_s3, s3_manager: S3Manager) -> None:
    """
    Uploads local files to an S3 bucket, with basic validation checks.

    :param s3_manager: utility for S3
    :param copy_local_to_s3: List of dictionaries containing local file metadata, where each dictionary has a "name" key.
    """
    num_files = len(copy_local_to_s3)

    if num_files > 0:
        print(f"Copying {num_files} local files up to S3")
        print_progress_bar(0, num_files, prefix='Progress:', suffix='Complete', length=50)

        for count, local_file in enumerate(copy_local_to_s3):
            file_key = local_file['name']

            # Validation checks
            if len(file_key) < 17:
                continue

            key_pathing, key_filename = os.path.split(file_key)
            if len(key_filename) < 15 or key_filename.endswith('/') or len(key_pathing) < 2:
                continue

            local_path = os.path.join('image_out', file_key)

            # Upload to S3
            s3_manager.upload_to_s3(local_path, file_key)  # This method handles exceptions

            print_progress_bar(count + 1, num_files, prefix='Progress:', suffix='Complete', length=50)


def synchronize_local_and_s3(s3_files: List[dict], local_files: List[dict], s3_manager: S3Manager):
    """
    From this we want to glean:
    - a list of files to rename in s3
    - a list of local files to rename
    - a list of files to copy local -> s3
    - a list of files to copy s3 -> local

    Note: local/s3 identical files aren't of interest for our purposes here.

    We will then do the operations necessary to get the two
    files systems in sync.

    :param local_files: list of local files as dict of 'name':str, 'size':int, 'last_modified':datetime
    :param s3_files: list of files from S3 as dict of 'name':str, 'size':int, 'last_modified':datetime
    :param s3_manager: You know, one of those things you use to manage S3 files.
    """
    # approximate key -> s3 file
    s3_dict = {
        create_approximating_key(file['name']): file for file in s3_files
    }
    # sort dict by key's value, just for human comprehension
    s3_dict = dict(sorted(s3_dict.items()))

    # approximate key -> local file
    local_dict = {
        create_approximating_key(file['name']): file for file in local_files
    }
    # sort dict by key's value, just for human comprehension
    local_dict = dict(sorted(local_dict.items()))

    # create sets using the approximate keys
    s3_approx_key_set = set(s3_dict.keys())
    local_approx_key_set = set(local_dict.keys())
    # difference the sets
    set_of_approx_only_in_s3 = s3_approx_key_set - local_approx_key_set
    set_of_approx_only_in_local = local_approx_key_set - s3_approx_key_set
    # intersection
    set_of_approx_in_both = s3_approx_key_set & local_approx_key_set

    print("Set information:")
    print(f"    {enforce_str_len('s3_approx_key_set')} contains {len(s3_approx_key_set)} files")
    print(f"    {enforce_str_len('local_approx_key_set')} contains {len(local_approx_key_set)} files")
    print(f"    {enforce_str_len('set_of_approx_only_in_s3')} contains {len(set_of_approx_only_in_s3)} files")
    print(f"    {enforce_str_len('set_of_approx_only_in_local')} contains {len(set_of_approx_only_in_local)} files")
    print(f"    {enforce_str_len('set_of_approx_in_both')} contains {len(set_of_approx_in_both)} files")

    # copy files up and copy files down
    copy_local_to_s3 = []  # use set_of_approx_only_in_local
    copy_s3_to_local = []  # use set_of_approx_only_in_s3

    for item in set_of_approx_only_in_local:
        copy_local_to_s3.append(local_dict[item])
    for item in set_of_approx_only_in_s3:
        copy_s3_to_local.append(s3_dict[item])

    upload_local_files_to_s3(copy_local_to_s3, s3_manager)

    #
    # # Copy up
    # num_files = len(copy_local_to_s3)
    # if num_files > 0:
    #     print(f"Copying {num_files} local files up to S3")
    #     print_progress_bar(0, num_files, prefix='Progress:', suffix='Complete', length=50)
    #     for count, local_file in enumerate(copy_local_to_s3):
    #         # validation...
    #         file_key = local_file['name']
    #         if len(file_key) < 17:
    #             continue
    #         key_pathing, key_filename = os.path.split(local_file['name'])
    #         if len(key_filename) < 15 or key_filename.endswith('/') or len(key_pathing) < 2:
    #             continue
    #         local_path = os.path.join('image_out', file_key)
    #         s3_manager.upload_to_s3(local_path, file_key)  # <-- consumes exceptions
    #         print_progress_bar(count + 1, num_files, prefix='Progress:', suffix='Complete', length=50)

    # Copy files down from s3
    # todo: make function that takes a max amount and a 'randomize' boolean, filter to specific directory/theme


    copy_s3_files_to_local(copy_s3_to_local, s3_manager, theme_name_filter="creative", max_to_copy=2)

    # num_files: int = len(copy_s3_to_local)
    # theme_name_filter: str = "creative"  # empty string means do not filter by theme
    # max_to_copy: int = 50  # special value 0 means copy all the files
    # randomize: bool = True
    #
    # if num_files > 0 and theme_name_filter and len(theme_name_filter) > 0:
    #     filtered_list = [item for item in copy_s3_to_local if item["name"].startswith(theme_name_filter)]
    #     num_files = len(filtered_list)
    #     if 0 == num_files:
    #         print(f"There are zero files in S3 for {theme_name_filter}")
    # else:
    #     filtered_list = copy_s3_to_local
    #
    # if num_files > 0:
    #     num_copied = 0
    #     if max_to_copy < 1:  # 0 means copy all files
    #         max_to_copy = num_files
    #     else:
    #         max_to_copy = min(max_to_copy, num_files)
    #     if randomize:
    #         random.shuffle(filtered_list)
    #     print(f"Copying {max_to_copy} files down from S3")
    #     print_progress_bar(0, max_to_copy, prefix='Progress:', suffix='Complete', length=50)
    #     for count, s3_file in enumerate(filtered_list):
    #         file_key: str = s3_file['name']
    #         # are we filtering by theme name? If so, skip any not in theme
    #         local_path = os.path.join('image_out', file_key)
    #         s3_manager.download_from_s3(file_key, local_path)
    #         num_copied += 1
    #         print_progress_bar(count + 1, max_to_copy, prefix='Progress:', suffix='Complete', length=50)
    #         if num_copied >= max_to_copy:
    #             break

    # look for files approximately in both that might
    # need renaming (e.g. the s3 version has a rating and
    # the local one doesn't.)
    # schema list of tuple(local-data, s3-data)
    rename_in_s3 = []
    rename_locally = []
    for item in set_of_approx_in_both:
        local_item = local_dict[item]
        s3_item = s3_dict[item]
        if local_item['name'] == s3_item['name']:
            continue
        # is there a rating in the local file? we'll want to re-name the s3 file
        match = re.search(r'r\[(\d+\.\d+)\]', str(local_item['name']))
        if match:
            rename_in_s3.append((local_item, s3_item))
            continue
        match = re.search(r'r\[(\d+\.\d+)\]', str(s3_item['name']))
        if match:
            rename_locally.append((local_item, s3_item))
            continue
        print(f"!!s3 and local filenames don't match:\n\t{local_item}\n\t{s3_item}")
    if len(rename_in_s3) > 0:
        print(f"\n-----\nthere are {len(rename_in_s3)} files to rename in S3:")
        for item in rename_in_s3:
            print(f"renaming S3 file '{item[1]['name']}' to local file's name, '{item[0]['name']}'")
            s3_manager.rename_s3_file(item[1]['name'], item[0]['name'])
    if len(rename_locally) > 0:
        print(f"\n-----\nthere are {len(rename_locally)} files to rename in S3:")
        for item in rename_locally:
            print(f"\n\trenaming local: {item[0]['name']}\n\t  to s3's filename: {item[1]['name']}")
            os.rename(f"image_out/{item[0]['name']}", f"image_out/{item[1]['name']}")

    # print("\ns3_approx_key_set:")
    # for item in s3_approx_key_set:
    #     print(f"    {enforce_str_len(item)}: {str(s3_dict[item])}")

    # for item in set_of_approx_only_in_local:
    #     the_tuple = (local_dict[item], s3_dict[item])
    #     copy_local_to_s3.append({item: the_tuple})
    #
    # print("\ns3_approx_key_set:")
    # for item in s3_approx_key_set:
    #     print(f"    {enforce_str_len(item)}: {str(s3_dict[item])}")
    #
    #
    # print("\ns3_approx_key_set:")
    # for item in local_approx_key_set:
    #     print(f"    {enforce_str_len(item)}: {str(local_dict[item])}")

    print("done")
    # mismatch_details = []
    # print(f"Iterating through the list of {len(mismatches)} mismatches")
    # for mismatch in mismatches:
    #     the_s3_match = s3_dict[mismatch]
    #     if not the_s3_match:
    #         print(f"mismatch key '{mismatch}' not found in s3_dict")
    #         continue
    #     the_local_match = local_dict[mismatch]
    #     if not the_local_match:
    #         print(f"mismatch key '{mismatch}' not found in the_local_match")
    #         continue
    #     print(f"mismatch key '{mismatch}':"
    #           f"\n\ts3 name:    '{the_s3_match['name']}'"
    #           f"\n\tlocal name: '{the_local_match['name']}'"
    #           )

    # s3_file = next((f for f in s3_files if
    #                 f['name'].startswith(mismatch[:mismatch.rfind('.')]) and f['name'].endswith(
    #                     mismatch[mismatch.rfind('.'):])), None)
    # local_file = next((f for f in local_files if
    #                    f['name'].startswith(mismatch[:mismatch.rfind('.')]) and f['name'].endswith(
    #                        mismatch[mismatch.rfind('.'):])), None)

    # if s3_file and local_file:
    #     mismatch_details.append({
    #         'approximate_match': mismatch,
    #         's3_name': s3_file['name'],
    #         'local_name': local_file['name']
    #     })


def print_mismatch_results(mismatch_details):
    print("\nFiles with naming mismatches (potential metadata differences):")
    for detail in mismatch_details:
        print(f"Approximate match: {detail['approximate_match']}")
        print(f"     S3 name: {detail['s3_name']}")
        print(f"  Local name: {detail['local_name']}")
        print()


def print_results(files_in_both, files_only_local, files_only_s3, match_mode):
    print(f"\nResults for {match_mode} matching:")
    print(f"Files in both: {len(files_in_both)}")
    print("  -", "\n  - ".join(files_in_both))

    print(f"\nFiles only local: {len(files_only_local)}")
    print("  -", "\n  - ".join(files_only_local))

    print(f"\nFiles only in S3: {len(files_only_s3)}")
    print("  -", "\n  - ".join(files_only_s3))


def save_results_to_file(files_in_both, files_only_local, files_only_s3, match_mode):
    with open(f"results_{match_mode}.txt", "w") as f:
        f.write(f"Results for {match_mode} matching:\n")
        f.write(f"Files in both: {len(files_in_both)}\n")
        f.write("  - " + "\n  - ".join(files_in_both) + "\n\n")

        f.write(f"Files only local: {len(files_only_local)}\n")
        f.write("  - " + "\n  - ".join(files_only_local) + "\n\n")

        f.write(f"Files only in S3: {len(files_only_s3)}\n")
        f.write("  - " + "\n  - ".join(files_only_s3))


def cleanse_s3_dupes(s3_files, s3: S3Manager) -> bool:
    """
    Ideally, there should only be one file for an approximate key in s3,
    but we have seen multiples. :/  For example:
    'creative/20250202T105414 output_image r[3.0].png'
    'creative/20250202T105414 prompt r[3.0].txt'
    'creative/20250202T105414 output_image.png'
    'creative/20250202T105414 prompt.txt'
    Looks like some deletes didn't happen on a rename/copy-delete
    operation. We'll fix that here.
    :return: True if any dupes were deleted, False otherwise.
    """
    # build dict of approx key to list of files in s3.
    akey_to_file_list = {}
    for item in s3_files:
        akey = create_approximating_key(item['name'])
        if len(akey) < 15 or akey.endswith('/'):
            continue
        if akey in akey_to_file_list:
            akey_to_file_list[akey].append(item)
        else:
            akey_to_file_list[akey] = [item]

    # for now, we will look for a rating and keep that, deleting the rest
    rating_pattern = re.compile(r' r\[(\d\.\d)\]')

    dupes_deleted = 0
    for akey, the_list in akey_to_file_list.items():
        if len(the_list) < 2:  # the list *should* be only 1 long
            continue
        item_with_rating = None
        print(f"\nFound dupes for approximate key '{akey}'")
        for dupe in the_list:
            this_one = " <-- will delete"
            if None == item_with_rating:
                match = rating_pattern.search(dupe['name'])
                if match:
                    item_with_rating = dupe
                    this_one = " <-- has rating; will save"
            print(f"\t{dupe['name']}{this_one}")
        print("\tdeletion commencing:")
        if item_with_rating:
            for dupe in the_list:
                if item_with_rating == dupe:
                    continue
                s3.delete_file(dupe['name'])
                print(f"\t\tdeleted: {dupe['name']}")
                dupes_deleted += 1
        else:
            print(f"Not sure what to delete; you should really look into it!")

    if dupes_deleted > 0:
        print(f"We deleted {dupes_deleted} dupes in s3")
        return True
    return False


def main():
    s3_manager = S3Manager()

    s3_files = s3_manager.list_files()
    any_deleted: bool = cleanse_s3_dupes(s3_files, s3_manager)
    if any_deleted:
        s3_files = s3_manager.list_files()

    local_files = list_local_files('image_out')

    synchronize_local_and_s3(s3_files, local_files, s3_manager)

    # # Perform exact matching
    # files_in_both_exact, files_only_local_exact, files_only_s3_exact = perform_set_operations(s3_files, local_files,
    #                                                                                           'exact')
    # # Perform approximate matching
    # files_in_both_approx, files_only_local_approx, files_only_s3_approx = perform_set_operations(s3_files, local_files,
    #                                                                                              'approximate')
    #
    # # Find naming mismatches
    #
    # # Print results
    # # print_results(files_in_both_exact, files_only_local_exact, files_only_s3_exact, 'exact')
    # # print_results(files_in_both_approx, files_only_local_approx, files_only_s3_approx, 'approximate')
    # print_mismatch_results(mismatch_details)
    #
    # # Save results to file
    # save_results_to_file(files_in_both_exact, files_only_local_exact, files_only_s3_exact, 'exact')
    # save_results_to_file(files_in_both_approx, files_only_local_approx, files_only_s3_approx, 'approximate')


if __name__ == "__main__":
    main()
