from chalice import Chalice, UnauthorizedError
import jwt
from chalicelib import storage_service
from chalicelib import recognition_service
from chalicelib import tts_service
from chalicelib import dynamo_service

import base64
import json

#####
# chalice app configuration
#####
app = Chalice(app_name='EmotSense')
app.debug = True
# Secret key used for JWT token encoding and decoding
SECRET_KEY = 'your_secret_key'
#####
# services initialization
#####
storage_location = 'contentcen301330426.aws.ai'
# target_image_storage =  'emotsense-target-images'
target_image_storage =  'contentcen301330426.aws.ai'

# user_reg_image_storage = 'emotsense-user-images'
user_reg_image_storage =  'contentcen301330426.aws.ai'

# user_auth_image_storage = 'emotsense-auth-images'
user_auth_image_storage =  'contentcen301330426.aws.ai'

storage_service = storage_service.StorageService()
recognition_service = recognition_service.RecognitionService(storage_service)
tts_service = tts_service.TTSService()
dynamo_service = dynamo_service.DynamoService()

# Decorator function to check JWT tokens
def jwt_auth_required(func):
    def wrapper(*args, **kwargs):
        token = app.current_request.json_body.get('token')
        if not token:
            raise UnauthorizedError("Authorization token is missing")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError("Token has expired")
        except jwt.InvalidTokenError:
            raise UnauthorizedError("Invalid token")
        return func(*args, **kwargs)
    return wrapper

#####
# RESTful endpoints
#####
@app.route('/images', methods = ['POST'], cors = True)
def upload_image():
    """processes file upload and saves file to storage service"""
    request_data = json.loads(app.current_request.raw_body)
    file_name = request_data['filename']
    file_bytes = base64.b64decode(request_data['filebytes'])
    storage = request_data['storage']
    image_info = storage_service.upload_file(file_bytes, file_name, storage)

    return image_info

# protected endpoint
@app.route('/images/{image_id}/detect-emotion', methods = ['POST'], cors = True)
@jwt_auth_required
def detect_emotion(image_id):
    print("User ID: ", payload['rekognitionId'])
    MIN_CONFIDENCE = 60.0

    emotions = []
    labels = recognition_service.detect_emotion(image_id, target_image_storage)
    for label in labels:
        print('-- ' + label['Type'] + ': ' + str(label['Confidence']))
        if label['Confidence'] > MIN_CONFIDENCE:
            emotions.append(label['Type'])
    return emotions

# protected endpoint
@app.route('/images/{image_id}/read', methods = ['POST'], cors = True)
@jwt_auth_required
def read_emotion(image_id):
    request_data = json.loads(app.current_request.raw_body)
    text = request_data['text']

    response = tts_service.synthesize_speech(text)
    audio_stream = response['AudioStream'].read()
    audio_info = storage_service.upload_file(audio_stream, image_id + ".mp3", target_image_storage)
    return audio_info

@app.route('/users', methods = ['POST'], cors = True)
def create_user():
    request_data = json.loads(app.current_request.raw_body)
    image_id = request_data['imageId']

    face_record = recognition_service.index_image(image_id, user_reg_image_storage)
    if face_record['ResponseMetadata']['HTTPStatusCode'] == 200:
        face_id = face_record['FaceRecords'][0]['Face']['FaceId']
        name = image_id.split('.')[0].split('_')
        first_name = name[0]
        last_name = name[1]
        response = dynamo_service.create_user(face_id, first_name, last_name)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return { 'message': "User successfully created."}
    return face_record

@app.route('/users/authenticate', methods = ['POST'], cors = True)
def authenticate_user():
    request_data = json.loads(app.current_request.raw_body)
    image_id = request_data['imageId']

    image_bytes = storage_service.file_bytes(image_id, user_auth_image_storage)
    matches = recognition_service.search_faces(image_bytes)

    for match in matches['FaceMatches']:
        print(match['Face']['FaceId'], match['Face']['Confidence'])

        face = dynamo_service.get_user(match['Face']['FaceId'])
        if 'Item' in face:
            print('Person Found: ', face['Item'])
            face['Item']['token'] = jwt.encode({'rekognitionId': face['Item']['rekognitionId']}, SECRET_KEY, algorithm='HS256')
            face['Item']['Message'] = "Success"
            return face['Item']
        
    return { 'Message': 'User not found' }

# protected endpoint
@app.route('/users/{face_id}/read_auth', methods = ['POST'], cors = True)
@jwt_auth_required
def read_emotion(face_id):
    print("User ID: ", payload['rekognitionId'])
    request_data = json.loads(app.current_request.raw_body)
    text = request_data['text']

    response = tts_service.synthesize_speech(text)
    audio_stream = response['AudioStream'].read()
    audio_info = storage_service.upload_file(audio_stream, face_id + ".mp3", user_auth_image_storage)
    return audio_info

# Error handler for UnauthorizedError
@app.route('/error', methods=['POST'])
def error_handler():
    return {'error': 'Unauthorized'}, 401