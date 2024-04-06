import boto3

class RecognitionService:
    def __init__(self, storage_service):
        self.client = boto3.client('rekognition')
        self.bucket_name = storage_service.get_storage_location()

    def detect_emotion(self, file_name):
        response = self.client.detect_faces(
            Image = {
                'S3Object': {
                    'Bucket': self.bucket_name,
                    'Name': file_name
                }
            },
            Attributes=['ALL',]
        )
        return response['FaceDetails'][0]['Emotions']