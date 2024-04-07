import boto3


class StorageService:
    def __init__(self):
        self.client = boto3.client('s3')
        
    def upload_file(self, file_bytes, file_name, bucket_name):
        self.client.put_object(Bucket = bucket_name,
                               Body = file_bytes,
                               Key = file_name,
                               ACL = 'public-read')

        return {'fileId': file_name,
                'fileUrl': "http://" + bucket_name + ".s3.amazonaws.com/" + file_name}

    def file_bytes(self, file_name, bucket_name):
        response = self.client.get_object(
            Bucket = bucket_name,
            Key = file_name
        )
        return response['Body'].read()