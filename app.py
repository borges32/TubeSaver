import argparse
import os
import shutil
import subprocess
import sys

try:
    import yt_dlp
    from yt_dlp.utils import DownloadError
except ImportError:
    print(
        "Dependência ausente: instale com `python3 -m pip install -r requirements.txt` "
        "ou execute com o Python do ambiente virtual."
    )
    sys.exit(1)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
)


def build_common_opts(output_path):
    os.makedirs(output_path, exist_ok=True)
    ydl_opts = {
        "outtmpl": os.path.join(output_path, "%(title)s.%(ext)s"),
        "user_agent": USER_AGENT,
        "noplaylist": True,
        "retries": 3,
        "extractor_args": {
            "youtube": {
                "player_client": ["web", "android", "ios"],
            }
        },
    }
    js_runtimes = {}
    node_path = shutil.which("node") or shutil.which("nodejs")
    deno_path = shutil.which("deno")
    if node_path:
        js_runtimes["node"] = {"path": node_path}
    if deno_path:
        js_runtimes["deno"] = {"path": deno_path}
    if js_runtimes:
        ydl_opts["js_runtimes"] = js_runtimes

    cookies_path = os.path.join(os.path.dirname(__file__), "cookies.txt")
    if os.path.exists(cookies_path):
        ydl_opts["cookiefile"] = cookies_path
    return ydl_opts


def download_youtube_audio(video_url, output_path):
    ydl_opts = build_common_opts(output_path)
    ydl_opts.update(
        {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }
    )
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])


def download_youtube_video(video_url, output_path, max_height=None):
    if max_height:
        video_format = (
            f"bestvideo*[height<={max_height}]+bestaudio/"
            f"best[height<={max_height}]/best"
        )
    else:
        video_format = "bestvideo*+bestaudio/best"

    ydl_opts = build_common_opts(output_path)
    ydl_opts.update(
        {
            "format": video_format,
            "merge_output_format": "mp4",
        }
    )
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])


def list_formats(video_url, output_path):
    ydl_opts = build_common_opts(output_path)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        for fmt in info.get("formats", []):
            format_id = fmt.get("format_id", "N/A")
            ext = fmt.get("ext", "N/A")
            note = fmt.get("format_note") or ""
            print(f"{format_id}: {ext} {note}".strip())


def convert_mp4_to_mp3(mp4_file_path, output_path):
    if not os.path.isfile(mp4_file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {mp4_file_path}")

    os.makedirs(output_path, exist_ok=True)
    base = os.path.splitext(os.path.basename(mp4_file_path))[0]
    mp3_file_path = os.path.join(output_path, f"{base}.mp3")
    cmd = [
        "ffmpeg",
        "-i",
        mp4_file_path,
        "-vn",
        "-ab",
        "192k",
        "-ar",
        "44100",
        "-y",
        mp3_file_path,
    ]
    subprocess.run(cmd, check=True)
    print(f"Convertido para MP3: {mp3_file_path}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Baixa vídeos/áudios do YouTube e converte MP4 para MP3."
    )
    parser.add_argument("url", help="URL do vídeo no YouTube ou caminho do MP4 local")
    parser.add_argument("tipo", choices=["mp3", "mp4", "mp4mp3", "list"])
    parser.add_argument(
        "--output",
        default="./",
        help="Diretório de saída (padrão: diretório atual)",
    )
    parser.add_argument(
        "--max-height",
        type=int,
        default=None,
        help="Limita a altura máxima do vídeo (ex.: 1080, 1440, 2160)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        if args.tipo == "mp3":
            download_youtube_audio(args.url, args.output)
        elif args.tipo == "mp4":
            download_youtube_video(args.url, args.output, args.max_height)
        elif args.tipo == "mp4mp3":
            convert_mp4_to_mp3(args.url, args.output)
        elif args.tipo == "list":
            list_formats(args.url, args.output)
    except DownloadError as exc:
        message = str(exc)
        if "Sign in to confirm you’re not a bot" in message:
            print(
                "Erro do YouTube: bloqueio anti-bot detectado. "
                "Exporte cookies para cookies.txt na pasta do projeto e tente novamente."
            )
        elif "This video is not available" in message:
            print(
                "Erro do YouTube: vídeo indisponível para extração no contexto atual. "
                "Se o vídeo abrir no navegador, tente adicionar cookies.txt e rode novamente."
            )
        else:
            print(f"Erro no download: {message}")
        return 1
    except FileNotFoundError as exc:
        print(str(exc))
        return 1
    except subprocess.CalledProcessError:
        print("Erro ao converter com ffmpeg. Verifique se o ffmpeg está instalado.")
        return 1
    except Exception as exc:
        print(f"Erro inesperado: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
