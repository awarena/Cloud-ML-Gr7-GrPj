import boto3

class RecognitionService:
    def __init__(self, storage_service):
        self.client = boto3.client('rekognition')
        self.collection_id = "users"
        self.ensure_collection_exists()

    def ensure_collection_exists(self):
        """Ensure the Rekognition collection exists, create if not."""
        try:
            # Attempt to describe the collection to check existence
            self.client.describe_collection(CollectionId=self.collection_id)
        except self.client.exceptions.ResourceNotFoundException:
            # If not found, create the collection
            print("Collection does not exist. Creating collection...")
            self.client.create_collection(CollectionId=self.collection_id)
            print("Collection created.")

    def detect_emotion(self, file_name, bucket_name):
        """Detect emotions in the image specified by file_name and bucket_name."""
        response = self.client.detect_faces(
            Image={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': file_name
                }
            },
            Attributes=['ALL',]
        )
        return response['FaceDetails'][0]['Emotions']
    
    def index_image(self, file_name, bucket_name):
        """Index an image by storing facial details in the collection."""
        response = self.client.index_faces(
            Image={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': file_name
                }
            },
            CollectionId=self.collection_id
        )
        return response
    
    def search_faces(self, face_bytes):
        """Search for faces matching the face_bytes in the collection."""
        response = self.client.search_faces_by_image(
            CollectionId=self.collection_id,
            Image={'Bytes': face_bytes}
        )
        return response
