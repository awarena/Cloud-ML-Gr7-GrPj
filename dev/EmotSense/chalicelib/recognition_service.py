import boto3

class RecognitionService:
    def __init__(self, storage_service):
        self.client = boto3.client('rekognition')
       
    def detect_emotion(self, file_name, bucket_name):
        response = self.client.detect_faces(
            Image = {
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': file_name
                }
            },
            Attributes=['ALL',]
        )
        return response['FaceDetails'][0]['Emotions']
    
    def index_image(self, file_name, bucket_name):
        response = self.client.index_faces(
            Image = {
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': file_name
                }
            },
            CollectionId="users"
            # aws rekognition create-collection --collection-id users --region us-east-1
        )
        return response
    
    def search_faces(self, face_bytes):
        response = self.client.search_faces_by_image(
            CollectionId='users',
            Image={'Bytes': face_bytes}
        )
        return response