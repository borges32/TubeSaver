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


if len(sys.argv) > 2:
    url = sys.argv[1]
    tipo = sys.argv[2]
    video_url = url
    output_path = "./"  # Diretório onde o arquivo MP3 será salvo
    
    if tipo == 'mp3':                        
        download_youtube_audio(video_url, output_path)
    elif tipo == 'mp4':
        download_youtube_video(video_url, output_path)
    elif tipo == 'list':
        list_formats(video_url)
        
        
else:
    print('Informa as parametro url do vídeo e forma mp3 ou mp4')


