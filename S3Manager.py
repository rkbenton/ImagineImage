import boto3
import os


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

    def upload_to_s3(self, file_path):
        """
        Uploads a given file to the specified S3 bucket.

        :param file_path: Path to the image file that needs to be uploaded.
        :return: None
        """
        file_name = os.path.basename(file_path)  # Extract just the filename from the full path

        try:
            # Attempt to upload the file to S3
            self.s3.upload_file(file_path, self.S3_BUCKET, file_name)
            print(f"✅ Uploaded {file_name} to S3 bucket: {self.S3_BUCKET}")
        except Exception as e:
            # Handle any errors that occur during the upload process
            print(f"❌ Upload to S3 failed: {e}")
