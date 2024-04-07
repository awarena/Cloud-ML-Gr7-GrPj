import boto3

class DynamoService:
    def __init__(self):
        self.client = boto3.resource('dynamodb')
        self.user_table = self.client.Table('users')

    def create_user(self, face_id, first_name, last_name):
        response = self.user_table.put_item(
            Item={
                'rekognitionId': face_id,
                'firstName': first_name,
                'lastName': last_name
            }
        )
        print("*"*30)
        print(response)
        return response
    
    def get_user(self, face_id):
        response = self.user_table.get_item(
            Key={
                'rekognitionId': face_id
            }
        )

        return response