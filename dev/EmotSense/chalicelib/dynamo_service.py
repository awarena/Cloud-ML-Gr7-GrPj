import boto3
from botocore.exceptions import ClientError

class DynamoService:
    def __init__(self):
        self.client = boto3.resource('dynamodb')
        self.table_name = 'users'
        self.user_table = self.client.Table(self.table_name)

        # Check if the table exists, create it if it doesn't
        if not self._table_exists(self.table_name):
            self._create_table()

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

    def _create_table(self):
        try:
            self.client.create_table(
                TableName=self.table_name,
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
