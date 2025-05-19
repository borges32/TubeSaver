import os
import sys
import subprocess
import yt_dlp


def download_youtube_audio(video_url, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',  # Nome do arquivo
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

def download_youtube_video(video_url, output_path):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',  # Forçar download do melhor formato disponível em MP4
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',  # Nome do arquivo baseado no título do vídeo
        'merge_output_format': 'mp4',  # Garantir que o formato final seja MP4
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'  # Converter para MP4 se necessário
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

def list_formats(video_url):
    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        formats = info.get('formats', [])
        for f in formats:
            print(f"{f['format_id']}: {f['ext']}")
            #print(f)

def convert_mp4_to_mp3(mp4_file_path, output_path='./'):
    """
    Converte um arquivo MP4 para MP3 usando ffmpeg.
    """
    if not os.path.isfile(mp4_file_path):
        print(f"Arquivo não encontrado: {mp4_file_path}")
        return

    base = os.path.splitext(os.path.basename(mp4_file_path))[0]
    mp3_file_path = os.path.join(output_path, f"{base}.mp3")
    cmd = [
        'ffmpeg',
        '-i', mp4_file_path,
        '-vn',
        '-ab', '192k',
        '-ar', '44100',
        '-y',
        mp3_file_path
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"Convertido para MP3: {mp3_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao converter: {e}")

if len(sys.argv) > 2:
    url = sys.argv[1]
    tipo = sys.argv[2]
    video_url = url
    output_path = "./"  # Diretório onde o arquivo MP3 será salvo
    
    if tipo == 'mp3':                        
        download_youtube_audio(video_url, output_path)
    elif tipo == 'mp4':
        download_youtube_video(video_url, output_path)  
    elif tipo == 'mp4mp3':
        # Converte um arquivo MP4 local para MP3
        convert_mp4_to_mp3(url, output_path)  
    elif tipo == 'list':
        list_formats(video_url)
        
        
else:
    print('Informa as parametro url do vídeo e forma mp3 ou mp4')


