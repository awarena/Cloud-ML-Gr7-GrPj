# tts_service.py
import boto3

class TTSService:
    def __init__(self):
        self.polly_client = boto3.client('polly')
        self.voice_id = 'Joanna'  # Choose a Polly voice (e.g., Joanna)

    def synthesize_speech(self, text):
        try:
            response = self.polly_client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=self.voice_id
            )

            # Save the synthesized speech to a file
            with open(f'{text}.mp3', 'wb') as f:
                f.write(response['AudioStream'].read())

            return f'{text}.mp3'
        except Exception as e:
            # Handle any exceptions
            print(f"Error synthesizing speech: {e}")
            return None