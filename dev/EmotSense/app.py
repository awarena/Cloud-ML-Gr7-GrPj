from chalice import Chalice
from chalicelib import storage_service
from chalicelib import recognition_service
from chalicelib import translation_service
from chalicelib import tts_service

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
storage_location = 'contentcen301228010.aws.ai'
storage_service = storage_service.StorageService(storage_location)
recognition_service = recognition_service.RecognitionService(storage_service)
translation_service = translation_service.TranslationService()
tts_service = tts_service.TTSService()


#####
# RESTful endpoints
#####
@app.route('/images', methods = ['POST'], cors = True)
def upload_image():
    """processes file upload and saves file to storage service"""
    request_data = json.loads(app.current_request.raw_body)
    file_name = request_data['filename']
    file_bytes = base64.b64decode(request_data['filebytes'])

    image_info = storage_service.upload_file(file_bytes, file_name)

    return image_info


@app.route('/images/{image_id}/detect-emotion', methods = ['POST'], cors = True)
def detect_emotion(image_id):
    """detects then translates text in the specified image"""
    request_data = json.loads(app.current_request.raw_body)
    from_lang = request_data['fromLang']
    to_lang = request_data['toLang']

    MIN_CONFIDENCE = 60.0

    emotions = []
    labels = recognition_service.detect_emotion(image_id)
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
    audio_info = storage_service.upload_file(audio_stream, image_id + ".mp3")
    return audio_info
