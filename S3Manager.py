import os

import boto3
from botocore.exceptions import ClientError


class S3Manager(object):
    """
    A class to manage S3 interactions, specifically uploading images to an S3 bucket.
    """

    # Define S3 bucket details (Ensure this bucket exists in your AWS account)
    S3_BUCKET = "im-im-images"  # Change to your bucket name
    AWS_REGION = "us-east-1"  # Change to your AWS region

    def __init__(self):
        """
        Initializes the S3Manager class by creating an S3 client.
        The client uses AWS credentials configured in the system.
        """
        self.s3 = boto3.client("s3")  # Initialize an S3 client using boto3

    def upload_to_s3(self, file_path, s3_key: str) -> None:
        """
        Uploads a given file to the specified S3 bucket.

        :param file_path: Path to the image file that needs to be uploaded.
        :param s3_key: S3 key to upload the file to, similar to a file path,
        e.g. "halloween/20250201T112210 output_image.png"
        :return: None
        """
        file_name = os.path.basename(file_path)  # Extract just the filename from the full path

        try:
            self.s3.upload_file(file_path, self.S3_BUCKET, s3_key)
            print(f"✅ Uploaded {file_name} to S3 bucket: {self.S3_BUCKET + '/' + s3_key}")
        except Exception as e:
            # Handle any errors that occur during the upload process
            print(f"❌ Upload of {file_name} to S3 failed: {e}")

    def download_from_s3(self, s3_key: str, local_file_path: str) -> None:
        """
        Download a file from S3 to a local path. Will create local directories
        as needed.

        :param s3_key: S3 key to download the file from, similar to a file path
        :param local_file_path: Local path to download the file to
        :return: None
        """
        try:
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

            self.s3.download_file(
                Bucket=self.S3_BUCKET,
                Key=s3_key,
                Filename=local_file_path
            )

            print(f"✅ Downloaded {s3_key} to : {local_file_path}")

        except ClientError as e:
            print(f"❌ Error downloading {s3_key} from S3: {e}")
        except Exception as e:
            print(f"❌ Unexpected error downloading {s3_key}: {e}")

    def list_files(self, extension=None, ascending=True):
        """
        Gets a list of all files in the S3 bucket, optionally filtered by extension
        and sorted by date.

        :param extension: File extension to filter by (e.g., '.jpg', '.png')
        :param ascending: Sort by date ascending if True, descending if False
        :return: List of dictionaries containing file info (name, size, last_modified)
        """
        try:
            # Get list of objects in the bucket
            paginator = self.s3.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.S3_BUCKET)

            files = []
            for page in pages:
                if 'Contents' not in page:
                    continue

                for obj in page['Contents']:
                    # If extension is specified, filter files
                    if extension:
                        if not obj['Key'].lower().endswith(extension.lower()):
                            continue

                    files.append({
                        'name': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified']
                    })

            # Sort files by last modified date
            files.sort(
                key=lambda x: x['last_modified'],
                reverse=not ascending
            )

            return files

        except Exception as e:
            print(f"❌ Failed to list files from S3: {e}")
            return []

    def is_in_s3(self, s3_prefix: str, filename: str) -> bool:
        cur_key = f"{s3_prefix}/{filename}"
        try:
            # Attempt to get metadata to check if the object exists
            self.s3.head_object(Bucket=self.S3_BUCKET, Key=cur_key)
            return True
        except self.s3.exceptions.ClientError as e:
            return False

    def delete_file(self, cur_key: str) -> bool:
        try:
            # Delete the original object
            self.s3.delete_object(
                Bucket=self.S3_BUCKET,
                Key=cur_key
            )
            return True
        except self.s3.exceptions.ClientError as e:
            print(f"failed to delete file: {e}")
            return False

    def rename_s3_file(self, old_key, new_key):
        """
        Similar to change_name_in_cloud, this version expects the
        keys to contain any pathing/prefixes, e.g. 'path/to/old_file.txt'.
        Raises an exception if the file does not exist in S3.
        """
        try:
            # Check if the object exists
            self.s3.head_object(Bucket=self.S3_BUCKET, Key=old_key)
        except self.s3.exceptions.ClientError as e:
            raise Exception(f"S3 file with key '{old_key}' does not exist.") from e

        # Copy the object to a new key
        self.s3.copy_object(
            Bucket=self.S3_BUCKET,
            CopySource={'Bucket': self.S3_BUCKET, 'Key': old_key},
            Key=new_key
        )

        # Delete the original object
        self.s3.delete_object(
            Bucket=self.S3_BUCKET,
            Key=old_key
        )

    def change_name_in_cloud(self, s3_prefix: str, cur_filename: str, new_filename: str):
        """
        Change the name (key) of a file in S3 from cur_key to new_key.
        Similar to rename_s3_file, this lets you specify the path/prefix and
        they filenames separately.
        Raises an exception if the file does not exist in S3.
        """
        cur_key = f"{s3_prefix}/{cur_filename}".replace("//", "/")
        new_key = f"{s3_prefix}/{new_filename}".replace("//", "/")
        print(f"S3: changing name from {cur_key} to {new_key}r4")
        try:
            # Check if the object exists
            self.s3.head_object(Bucket=self.S3_BUCKET, Key=cur_key)
        except self.s3.exceptions.ClientError as e:
            raise Exception(f"S3 file with key '{cur_key}' does not exist.") from e

        # Copy the object to the new key
        copy_source = {'Bucket': self.S3_BUCKET, 'Key': cur_key}
        self.s3.copy_object(Bucket=self.S3_BUCKET, CopySource=copy_source, Key=new_key)
        # Delete the old object
        self.s3.delete_object(Bucket=self.S3_BUCKET, Key=cur_key)
