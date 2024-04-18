from chalice import Chalice
from chalicelib import storage_service
from chalicelib import recognition_service
from chalicelib import translation_service
from chalicelib import tts_service
from chalicelib import dynamo_service

import base64
import json

#####
# chalice app configuration
#####
app = Chalice(app_name='EmotSense')
app.debug = True

#####
# services initialization
#####
storage_location = 'contentcen301232634.aws.ai'
# target_image_storage =  'emotsense-target-images'
target_image_storage =  'contentcen301232634.aws.ai'

# user_reg_image_storage = 'emotsense-user-images'
user_reg_image_storage =  'contentcen301232634.aws.ai'

# user_auth_image_storage = 'emotsense-auth-images'
user_auth_image_storage =  'contentcen301232634.aws.ai'

storage_service = storage_service.StorageService()
recognition_service = recognition_service.RecognitionService(storage_service)
translation_service = translation_service.TranslationService()
tts_service = tts_service.TTSService()
dynamo_service = dynamo_service.DynamoService()


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


@app.route('/images/{image_id}/detect-emotion', methods = ['POST'], cors = True)
def detect_emotion(image_id):
    """detects then translates text in the specified image"""
    request_data = json.loads(app.current_request.raw_body)
    from_lang = request_data['fromLang']
    to_lang = request_data['toLang']

    MIN_CONFIDENCE = 60.0

    emotions = []
    labels = recognition_service.detect_emotion(image_id, target_image_storage)
    for label in labels:
        print('-- ' + label['Type'] + ': ' + str(label['Confidence']))
        if label['Confidence'] > MIN_CONFIDENCE:
            emotions.append(label['Type'])
    return emotions

@app.route('/images/{image_id}/read', methods = ['POST'], cors = True)
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
            face['Item']['Message'] = "Success"
            return face['Item']
        
    return { 'Message': 'User not found' }

@app.route('/users/{face_id}/read_auth', methods = ['POST'], cors = True)
def read_emotion(face_id):
    request_data = json.loads(app.current_request.raw_body)
    text = request_data['text']

    response = tts_service.synthesize_speech(text)
    audio_stream = response['AudioStream'].read()
    audio_info = storage_service.upload_file(audio_stream, face_id + ".mp3", user_auth_image_storage)
    return audio_info
