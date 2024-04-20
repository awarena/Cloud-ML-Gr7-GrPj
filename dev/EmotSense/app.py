from chalice import Chalice, Response
from chalicelib import storage_service, recognition_service, tts_service, dynamo_service
import jwt
import datetime
import base64
import json

# Chalice app configuration
app = Chalice(app_name='EmotSense')
app.debug = True

# Secret key for JWT, should be kept secure
SECRET_KEY = 'your_secret_key'

# Services initialization
storage_location = 'contentcen301330426.aws.ai'
storage_service = storage_service.StorageService(storage_location)
recognition_service = recognition_service.RecognitionService(storage_location)
tts_service = tts_service.TTSService()
dynamo_service = dynamo_service.DynamoService()

# Function to decode the JWT and extract the user
def get_current_user():
    token = app.current_request.headers.get('Authorization')
    if not token:
        return None

    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None  # or you might raise an exception or return an error response
    except jwt.InvalidTokenError:
        return None  # Handle invalid token

# Protected route that requires valid JWT to access
@app.route('/protected', methods=['GET'], cors=True)
def protected():
    user = get_current_user()
    if not user:
        return Response(body={'message': 'Unauthorized'}, status_code=401)
    return {'message': 'This is a protected route'}

# New Endpoint to generate JWT
@app.route('/generate_jwt', methods=['POST'], cors=True)
def generate_jwt():
    """ Endpoint to generate a JWT for testing. """
    request = app.current_request
    username = request.json_body.get('username', None)
    password = request.json_body.get('password', None)

    if username == 'admin' and password == 'secret':
        payload = {
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return {'jwt': token}
    else:
        return Response(body={'message': 'Unauthorized'}, status_code=401)

# New Endpoint to verify JWT
@app.route('/verify_jwt', methods=['POST'], cors=True)
def verify_jwt():
    """ Endpoint to verify a JWT for testing. """
    request = app.current_request
    token = request.json_body.get('token', None)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return {'message': 'JWT is valid', 'payload': payload}
    except jwt.ExpiredSignatureError:
        return Response(body={'message': 'Token expired'}, status_code=401)
    except jwt.InvalidTokenError:
        return Response(body={'message': 'Invalid token'}, status_code=401)

# RESTful endpoints
@app.route('/images', methods=['POST'], cors=True)
def upload_image():
    """Processes file upload and saves file to storage service"""
    request_data = json.loads(app.current_request.raw_body)
    file_name = request_data['filename']
    file_bytes = base64.b64decode(request_data['filebytes'])
    folder = request_data['folder']
    image_info = storage_service.upload_file(file_bytes, file_name, folder)
    return image_info

@app.route('/images/{image_id}/detect-emotion', methods=['POST'], cors=True)
def detect_emotion(image_id):
    """Detects then translates text in the specified image"""
    request_data = json.loads(app.current_request.raw_body)
    rekognitionId = request_data['rekognitionId']
    folder = request_data['folder']
    MIN_CONFIDENCE = 60.0
    emotions = []
    labels = recognition_service.detect_emotion(image_id, folder)
    for label in labels:
        print('-- ' + label['Type'] + ': ' + str(label['Confidence']))
        if label['Confidence'] > MIN_CONFIDENCE:
            emotions.append(label['Type'])

    dynamo_service.log_emotions(rekognitionId, emotions)  ### call the log_emotions method from dynamo_service.pyßß
    return emotions

@app.route('/images/{image_id}/read', methods=['POST'], cors=True)
def read_emotion(image_id):
    request_data = json.loads(app.current_request.raw_body)
    text = request_data['text']
    response = tts_service.synthesize_speech(text)
    audio_stream = response['AudioStream'].read()
    audio_info = storage_service.upload_file(audio_stream, image_id + ".mp3", "emotions")
    return audio_info

@app.route('/users', methods=['POST'], cors=True)
def create_user():
    request_data = json.loads(app.current_request.raw_body)
    image_id = request_data['imageId']
    folder = request_data['folder']
    face_record = recognition_service.index_image(image_id, folder)
    if face_record['ResponseMetadata']['HTTPStatusCode'] == 200:
        face_id = face_record['FaceRecords'][0]['Face']['FaceId']
        name = image_id.split('.')[0].split('_')
        first_name = name[0]
        last_name = name[1]
        response = dynamo_service.create_user(face_id, first_name, last_name)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return {'message': "User successfully created."}
    return face_record

@app.route('/users/authenticate', methods=['POST'], cors=True)
def authenticate_user():
    request_data = json.loads(app.current_request.raw_body)
    image_id = request_data['imageId']
    folder = request_data['folder']
    image_bytes = storage_service.file_bytes(image_id, folder)
    matches = recognition_service.search_faces(image_bytes)
    for match in matches['FaceMatches']:
        print(match['Face']['FaceId'], match['Face']['Confidence'])
        face = dynamo_service.get_user(match['Face']['FaceId'])
        if 'Item' in face:
            print('Person Found: ', face['Item'])
            payload = {
                'face': face['Item']['rekognitionId'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            face['Item']['Message'] = "Success"
            face['Item']['token'] = token
            return face['Item']
    return {'Message': 'User not found'}

@app.route('/users/{face_id}/read_auth', methods=['POST'], cors=True)
def read_auth(face_id):
    request_data = json.loads(app.current_request.raw_body)
    text = request_data['text']
    response = tts_service.synthesize_speech(text)
    audio_stream = response['AudioStream'].read()
    audio_info = storage_service.upload_file(audio_stream, face_id + ".mp3", "authenticate")
    return audio_info