import yt_dlp
import boto3
import os
from credenciales import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_SESSION_TOKEN, REGION, BUCKET_NAME

ARCHIVO_LINKS_A = 'links_cuenta_A.txt'
ARCHIVO_LINKS_B = 'links_cuenta_B.txt'

CARPETA_S3_A = 'cuenta_a/'
CARPETA_S3_B = 'cuenta_b/'

def get_s3_client():
    return boto3.client('s3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        aws_session_token=AWS_SESSION_TOKEN,
        region_name=REGION
    )

def subir_a_s3(local_file, s3_folder):
    s3 = get_s3_client()
    filename = os.path.basename(local_file)
    s3_key = f"{s3_folder}{filename}"
    
    try:
        print(f"   ☁️ Subiendo a S3: {s3_key}...")
        s3.upload_file(local_file, BUCKET_NAME, s3_key)
        os.remove(local_file) 
        print("   🗑️ Eliminado de Ubuntu (Limpieza).")
    except Exception as e:
        print(f"   ❌ Error subiendo a S3: {e}")

def procesar_lista(archivo_txt, carpeta_s3):
    print(f"\n🚀 PROCESANDO LISTA: {archivo_txt}")
    if not os.path.exists(archivo_txt):
        print(f"⚠️ FALTA EL ARCHIVO: {archivo_txt}")
        return

    with open(archivo_txt, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    print(f"   -> Encontrados {len(urls)} links.")
    
    # Configuración yt-dlp
    opciones = {
        'format': 'mp4',
        'outtmpl': 'video_temp_%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
    }

    with yt_dlp.YoutubeDL(opciones) as ydl:
        for i, url in enumerate(urls):
            print(f"   [{i+1}/{len(urls)}] Descargando...")
            try:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if os.path.exists(filename):
                    subir_a_s3(filename, carpeta_s3)
            except Exception as e:
                print(f"   ❌ Fallo descarga: {e}")

def main():
    procesar_lista(ARCHIVO_LINKS_A, CARPETA_S3_A)
    procesar_lista(ARCHIVO_LINKS_B, CARPETA_S3_B)
    print("\n✨ CARGA COMPLETA. Ahora ejecuta 'python3 main.py'")

if __name__ == "__main__":
    main()