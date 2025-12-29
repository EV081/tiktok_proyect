from aws_client import AWSAnalyzer
import metrics
import boto3
from credenciales import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_SESSION_TOKEN, REGION, BUCKET_NAME

CARPETA_A = 'cuenta_a/'
CARPETA_B = 'cuenta_b/'

def obtener_videos_de_carpeta(folder_prefix):
    s3 = boto3.client('s3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        aws_session_token=AWS_SESSION_TOKEN,
        region_name=REGION
    )
    videos = []
    print(f"📂 Escaneando S3: {folder_prefix}...")
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=folder_prefix)
        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'].endswith('.mp4'): 
                    videos.append(obj['Key'])
        print(f"   -> {len(videos)} videos encontrados.")
        return videos
    except Exception as e:
        print(f"   ❌ Error leyendo S3 (¿Credenciales expiradas?): {e}")
        return []

def procesar_perfil(bot, lista_videos, nombre):
    print(f"\n--- 🧠 Analizando {nombre} ---")
    vis, aud, tex = set(), set(), set()

    for i, video in enumerate(lista_videos):
        print(f"[{i+1}/{len(lista_videos)}] {video.split('/')[-1]}...")
        vis.update(bot.analizar_video_visual(video))
        aud.update(bot.analizar_audio_texto(video))
        tex.update(bot.analizar_texto_video(video))
    
    return vis, aud, tex

def main():
    try:
        bot = AWSAnalyzer()
    except Exception as e:
        print("❌ Error de Credenciales: Revisa credenciales.py")
        return

    # 1. Detectar videos
    videos_A = obtener_videos_de_carpeta(CARPETA_A)
    videos_B = obtener_videos_de_carpeta(CARPETA_B)

    if not videos_A: return

    # 2. Procesar
    vis_A, aud_A, tex_A = procesar_perfil(bot, videos_A, "Perfil A")
    vis_B, aud_B, tex_B = procesar_perfil(bot, videos_B, "Perfil B")

    # 3. Métricas
    print("\n--- 🧮 Calculando Compatibilidad... ---")
    s_v, c_v = metrics.indice_jaccard(vis_A, vis_B)
    s_a, c_a = metrics.indice_jaccard(aud_A, aud_B)
    s_t, c_t = metrics.indice_jaccard(tex_A, tex_B)

    # 4. Reporte
    metrics.reporte(s_v, s_a, s_t, c_v, c_a, c_t)

if __name__ == "__main__":
    main()