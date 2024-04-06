# tts_service.py
import boto3

class TTSService:
    def __init__(self):
        self.client = boto3.client('polly')
        self.voice_id = 'Joanna'  # Choose a Polly voice (e.g., Joanna)

    def synthesize_speech(self, text):
        try:
            response = self.client.synthesize_speech(
                VoiceId=self.voice_id,
                OutputFormat='mp3', 
                Text = text,
                Engine = 'neural')
        except boto3.exceptions.ClientError as error:
            raise error
        return response