import boto3
import time
import json
import urllib.request
from credenciales import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_SESSION_TOKEN, REGION, BUCKET_NAME

class AWSAnalyzer:
    def __init__(self):
        self.bucket = BUCKET_NAME
        
        self.session = boto3.Session(
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            aws_session_token=AWS_SESSION_TOKEN,
            region_name=REGION
        )
        
        self.rekognition = self.session.client('rekognition')
        self.transcribe = self.session.client('transcribe')
        self.s3 = self.session.client('s3')


    def analizar_video_visual(self, video_filename):
        print(f"   [👁️] Rekognition: Analizando objetos en {video_filename}...")
        try:
            response = self.rekognition.start_label_detection(
                Video={'S3Object': {'Bucket': self.bucket, 'Name': video_filename}},
                MinConfidence=70
            )
            job_id = response['JobId']
            while True:
                status = self.rekognition.get_label_detection(JobId=job_id)
                if status['JobStatus'] in ['SUCCEEDED', 'FAILED']: break
                time.sleep(2)
            
            if status['JobStatus'] == 'SUCCEEDED':
                return set([item['Label']['Name'] for item in status['Labels']])
            return set()
        except Exception as e:
            print(f"   ❌ Error Visual: {e}")
            return set()

    # --- 2. AUDIO (Voz a Texto) ---
    def analizar_audio_texto(self, video_filename):
        print(f"   [🎤] Transcribe: Escuchando {video_filename}...")
        job_name = f"job_{int(time.time())}_{video_filename.split('/')[-1][-10:-4]}"
        video_uri = f"s3://{self.bucket}/{video_filename}"
        
        try:
            self.transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': video_uri},
                MediaFormat='mp4',
                LanguageCode='es-ES'
            )
            while True:
                status = self.transcribe.get_transcription_job(TranscriptionJobName=job_name)
                if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']: break
                time.sleep(2)
                
            if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
                uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
                with urllib.request.urlopen(uri) as url:
                    data = json.loads(url.read().decode())
                    texto = data['results']['transcripts'][0]['transcript']
                    return set([w.lower() for w in texto.split() if len(w) > 4])
            return set()
        except Exception as e:
            print(f"   ⚠️ Aviso: Sin audio detectable.")
            return set()

    # --- 3. TEXTO (OCR - Lectura en pantalla) ---
    def analizar_texto_video(self, video_filename):
        print(f"   [🔤] OCR: Leyendo texto en pantalla...")
        try:
            response = self.rekognition.start_text_detection(
                Video={'S3Object': {'Bucket': self.bucket, 'Name': video_filename}},
                Filters={'WordFilter': {'MinConfidence': 80}}
            )
            job_id = response['JobId']
            while True:
                status = self.rekognition.get_text_detection(JobId=job_id)
                if status['JobStatus'] in ['SUCCEEDED', 'FAILED']: break
                time.sleep(2)
            
            if status['JobStatus'] == 'SUCCEEDED':
                texto = set()
                for item in status['TextDetections']:
                    if item['TextDetection']['Type'] == 'LINE' and len(item['TextDetection']['DetectedText']) > 3:
                        texto.add(item['TextDetection']['DetectedText'].lower())
                return texto
            return set()
        except Exception as e:
            print(f"   ❌ Error OCR: {e}")
            return set()