from aws_client import AWSAnalyzer
import metrics
import boto3

# --- CONFIGURACIÓN ---
BUCKET = 'proyect-tiktok-vssz'  # <--- ¡PON TU BUCKET AQUÍ!
CARPETA_A = 'cuenta_a/'
CARPETA_B = 'cuenta_b/'

def obtener_videos_de_carpeta(bucket_name, folder_prefix):
    s3 = boto3.client('s3', region_name='us-east-1')
    videos = []
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)
        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'].endswith('.mp4'): 
                    videos.append(obj['Key'])
        return videos
    except Exception as e:
        print(f"Error S3: {e}")
        return []

def procesar_perfil(bot, lista_videos, nombre_perfil):
    print(f"\n--- 🧠 Analizando {nombre_perfil} ({len(lista_videos)} videos) ---")
    visual = set()
    audio = set()
    texto = set()

    for i, video in enumerate(lista_videos):
        print(f"[{i+1}/{len(lista_videos)}] Procesando: {video.split('/')[-1]} ...")
        
        # 1. VISUAL
        visual.update(bot.analizar_video_visual(video))
        # 2. AUDIO
        audio.update(bot.analizar_audio_texto(video))
        # 3. TEXTO (OCR)
        texto.update(bot.analizar_texto_video(video))
    
    return visual, audio, texto

def main():
    bot = AWSAnalyzer(BUCKET)
    
    # 1. Detectar videos en S3
    videos_A = obtener_videos_de_carpeta(BUCKET, CARPETA_A)
    videos_B = obtener_videos_de_carpeta(BUCKET, CARPETA_B)

    if not videos_A or not videos_B:
        print("⚠️ No hay videos en S3. Ejecuta primero 'ingesta_txt.py'")
        return

    # 2. Procesar Perfiles
    vis_A, aud_A, tex_A = procesar_perfil(bot, videos_A, "Perfil A")
    vis_B, aud_B, tex_B = procesar_perfil(bot, videos_B, "Perfil B")

    # 3. Calcular Métricas
    print("\n--- 🧮 Calculando resultados... ---")
    s_v, c_v = metrics.indice_jaccard(vis_A, vis_B)
    s_a, c_a = metrics.indice_jaccard(aud_A, aud_B)
    s_t, c_t = metrics.indice_jaccard(tex_A, tex_B)

    # 4. Generar Reporte
    metrics.reporte(s_v, s_a, s_t, c_v, c_a, c_t)

if __name__ == "__main__":
    main()