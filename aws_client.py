import boto3
import time
import json
import urllib.request

class AWSAnalyzer:
    def __init__(self, bucket_name, region='us-east-1'):
        self.bucket = bucket_name
        # Al usar LabInstanceProfile, no necesitamos poner claves aquí
        self.rekognition = boto3.client('rekognition', region_name=region)
        self.transcribe = boto3.client('transcribe', region_name=region)
        self.s3 = boto3.client('s3', region_name=region)

    def analizar_video_visual(self, video_filename):
        print(f"   [👁️] Rekognition Labels: Analizando objetos en {video_filename}...")
        try:
            response = self.rekognition.start_label_detection(
                Video={'S3Object': {'Bucket': self.bucket, 'Name': video_filename}},
                MinConfidence=70
            )
            job_id = response['JobId']
            
            while True:
                status = self.rekognition.get_label_detection(JobId=job_id)
                if status['JobStatus'] in ['SUCCEEDED', 'FAILED']:
                    break
                time.sleep(2)
            
            if status['JobStatus'] == 'SUCCEEDED':
                etiquetas = set()
                for item in status['Labels']:
                    etiquetas.add(item['Label']['Name'])
                return etiquetas
            else:
                return set()
        except Exception as e:
            print(f"   ❌ Error Visual: {e}")
            return set()

    # --- 2. AUDIO (Transcribe a Texto) ---
    def analizar_audio_texto(self, video_filename):
        print(f"   [🎤] Transcribe: Escuchando {video_filename}...")
        job_name = f"job_{int(time.time())}_{video_filename.split('/')[-1][-10:-4]}"
        video_uri = f"s3://{self.bucket}/{video_filename}"
        
        try:
            self.transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': video_uri},
                MediaFormat='mp4',
                LanguageCode='es-ES' # Cambia a 'en-US' si los videos son en inglés
            )
            
            while True:
                status = self.transcribe.get_transcription_job(TranscriptionJobName=job_name)
                state = status['TranscriptionJob']['TranscriptionJobStatus']
                if state in ['COMPLETED', 'FAILED']:
                    break
                time.sleep(2)
                
            if state == 'COMPLETED':
                uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
                with urllib.request.urlopen(uri) as url:
                    data = json.loads(url.read().decode())
                    texto = data['results']['transcripts'][0]['transcript']
                    # Filtramos palabras cortas (>4 letras)
                    return set([w.lower() for w in texto.split() if len(w) > 4])
            return set()
        except Exception as e:
            # Muchos TikToks no tienen audio o solo música, es normal que falle
            print(f"   ⚠️ Aviso: Video sin voz detectable o error de Transcribe.")
            return set()

    # --- 3. TEXTO EN PANTALLA (OCR) ---
    def analizar_texto_video(self, video_filename):
        print(f"   [🔤] Rekognition Text: Leyendo letreros/subtítulos...")
        try:
            response = self.rekognition.start_text_detection(
                Video={'S3Object': {'Bucket': self.bucket, 'Name': video_filename}},
                Filters={'WordFilter': {'MinConfidence': 80}}
            )
            job_id = response['JobId']
            
            while True:
                status = self.rekognition.get_text_detection(JobId=job_id)
                if status['JobStatus'] in ['SUCCEEDED', 'FAILED']:
                    break
                time.sleep(2)
            
            if status['JobStatus'] == 'SUCCEEDED':
                texto_encontrado = set()
                for item in status['TextDetections']:
                    if item['TextDetection']['Type'] == 'LINE':
                        frase = item['TextDetection']['DetectedText']
                        if len(frase) > 3: 
                            texto_encontrado.add(frase.lower())
                return texto_encontrado
            return set()
        except Exception as e:
            print(f"   ❌ Error OCR: {e}")
            return set()