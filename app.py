import yt_dlp
import sys

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
        'format': 'best[ext=mp4]',  # Forçar download do melhor formato disponível em MP4
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',  # Nome do arquivo baseado no título do vídeo
        'merge_output_format': 'mp4',  # Garantir que o formato final seja MP4
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'  # Converter para MP4 se necessário
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])


if len(sys.argv) > 2:
    url = sys.argv[1]
    tipo = sys.argv[2]
    video_url = url
    output_path = "./"  # Diretório onde o arquivo MP3 será salvo
    
    if tipo == 'mp3':                        
        download_youtube_audio(video_url, output_path)
    else:
        download_youtube_video(video_url, output_path)
        
        
else:
    print('Informa as parametro url do vídeo e forma mp3 ou mp4')


