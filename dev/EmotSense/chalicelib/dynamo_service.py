import boto3
from botocore.exceptions import ClientError
import time ### added time module to log timestamp
import uuid ### to generate unique id (for emotion logs)

class DynamoService:
    def __init__(self):
        self.client = boto3.resource('dynamodb')
        self.table_name = 'users'
        self.emotion_logs_table_name = 'emotion_logs' ### new table to log emotions
        self.user_table = self.client.Table(self.table_name)
        self.emotion_logs_table = self.client.Table(self.emotion_logs_table_name) ### table object for emotion_logs
        # Check if the table exists, create it if it doesn't
        if not self._table_exists(self.table_name):
            self._create_table(self.table_name)
        ### Check if the emotion_logs table exists, create it if it doesn't
        if not self._table_exists(self.emotion_logs_table_name):
            self._create_emotion_logs_table()           

    def _table_exists(self, table_name):
        try:
            self.client.Table(table_name).load()
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return False
            else:
                raise
        else:
            return True

    def _create_table(self, table_name): ### added table_name parameter for emotion_logs table
        try:
            self.client.create_table(
                TableName=table_name, ### changed self.table_name to table_name for emotion_logs table
                KeySchema=[
                    {
                        'AttributeName': 'rekognitionId',
                        'KeyType': 'HASH'  # Partition key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'rekognitionId',
                        'AttributeType': 'S'  # String
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
        except ClientError as e:
            print(f"Error creating DynamoDB table: {e}")
            raise

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
    

    ### method to create emotion_logs table
    ### will be called in __init__ if table does not exist
    def _create_emotion_logs_table(self):
        try:
            self.client.create_table(
                TableName=self.emotion_logs_table_name,
                KeySchema=[
                    {
                        'AttributeName': 'logId',
                        'KeyType': 'HASH'  # Partition key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'logId',
                        'AttributeType': 'S'  # String
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
        except ClientError as e:
            print(f"Error creating DynamoDB table: {e}")
            raise

    ### method to log emotions, called from app.py ###
    def log_emotions(self, rekognitionId, emotions):
        logId = str(uuid.uuid4())  # create unique log ID 
        timestamp = int(time.time())  # unix timestamp
        try:
            self.emotion_logs_table.put_item(
                Item={
                    'logId': logId,
                    'rekognitionId': rekognitionId,
                    'emotions': emotions,
                    'timestamp': timestamp 
                }
            )
        except ClientError as e:
            print(f"Error logging emotions: {e}")
            raise