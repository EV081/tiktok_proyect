import yt_dlp
import boto3
import os

# --- CONFIGURACIÓN ---
BUCKET_NAME = 'proyect-tiktok-vssz'

# Archivos de texto
ARCHIVO_LINKS_A = 'links_cuenta_A.txt'
ARCHIVO_LINKS_B = 'links_cuenta_B.txt'

CARPETA_S3_A = 'cuenta_a/'
CARPETA_S3_B = 'cuenta_b/'

def subir_a_s3(local_file, s3_folder):
    s3 = boto3.client('s3', region_name='us-east-1')
    filename = os.path.basename(local_file)
    s3_key = f"{s3_folder}{filename}"
    
    try:
        print(f"   ☁️ Subiendo a S3: {s3_key}...")
        s3.upload_file(local_file, BUCKET_NAME, s3_key)
        os.remove(local_file) 
        print("   🗑️ Archivo local eliminado.")
    except Exception as e:
        print(f"   ❌ Error subiendo a S3: {e}")

def procesar_lista(archivo_txt, carpeta_s3):
    print(f"\n🚀 PROCESANDO LISTA: {archivo_txt}")
    
    if not os.path.exists(archivo_txt):
        print(f"⚠️ El archivo {archivo_txt} no existe. Créalo con 'nano' y pega los links.")
        return

    with open(archivo_txt, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    print(f"   -> Se encontraron {len(urls)} links.")

    opciones = {
        'format': 'mp4',
        'outtmpl': 'video_temp_%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
    }

    with yt_dlp.YoutubeDL(opciones) as ydl:
        for i, url in enumerate(urls):
            print(f"   [{i+1}/{len(urls)}] Descargando: {url}")
            try:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if os.path.exists(filename):
                    subir_a_s3(filename, carpeta_s3)
            except Exception as e:
                print(f"   ❌ Falló descarga: {e}")

def main():
    procesar_lista(ARCHIVO_LINKS_A, CARPETA_S3_A)
    procesar_lista(ARCHIVO_LINKS_B, CARPETA_S3_B)
    print("\n✨ INGESTA TERMINADA. Ejecuta 'python3 main.py' ahora.")

if __name__ == "__main__":
    main()