import boto3


class StorageService:
    def __init__(self, storage_location):
        self.client = boto3.client('s3')
        self.bucket_name = storage_location
    def upload_file(self, file_bytes, file_name, folder):
        key = f"{folder}/{file_name}" 
        self.client.put_object(Bucket = self.bucket_name,
                               Body = file_bytes,
                               Key = key,
                               ACL = 'public-read')

        return {'fileId': file_name,
                'fileUrl': "http://" + self.bucket_name + ".s3.amazonaws.com/" + key,
                'folder': folder}

    def file_bytes(self, file_name, folder):
        key = f"{folder}/{file_name}"
        response = self.client.get_object(
            Bucket = self.bucket_name,
            Key = key
        )
        return response['Body'].read()