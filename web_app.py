from flask import Flask, render_template, request, send_file, redirect, url_for, after_this_request, flash, session
import os
import shutil
import yt_dlp
import uuid
from yt_dlp.utils import DownloadError

app = Flask(__name__)
app.secret_key = 'supersecretkey'
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'

# Funções de download

def build_common_opts(output_path):
    os.makedirs(output_path, exist_ok=True)
    ydl_opts = {
        'outtmpl': f'{output_path}/%(title)s_%(id)s.%(ext)s',
        'user_agent': USER_AGENT,
        'noplaylist': True,
        'retries': 3,
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'android', 'ios'],
            }
        },
    }
    js_runtimes = {}
    node_path = shutil.which('node') or shutil.which('nodejs')
    deno_path = shutil.which('deno')
    if node_path:
        js_runtimes['node'] = {'path': node_path}
    if deno_path:
        js_runtimes['deno'] = {'path': deno_path}
    if js_runtimes:
        ydl_opts['js_runtimes'] = js_runtimes

    cookies_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')
    if os.path.exists(cookies_path):
        ydl_opts['cookiefile'] = cookies_path
    return ydl_opts


def download_youtube_audio(video_url, output_path):
    ydl_opts = build_common_opts(output_path)
    ydl_opts.update({
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    })
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url)
        filename = ydl.prepare_filename(info)
        base, _ = os.path.splitext(filename)
        return base + '.mp3'

def download_youtube_video(video_url, output_path, max_height=None):
    if max_height:
        format_candidates = [
            f'bestvideo*[height<={max_height}]+bestaudio',
            f'best*[height<={max_height}]',
            f'best[height<={max_height}]',
            'bestvideo*+bestaudio',
            'best',
        ]
    else:
        format_candidates = [
            'bestvideo*+bestaudio',
            'bestvideo+bestaudio',
            'best',
        ]

    last_format_error = None
    for video_format in format_candidates:
        ydl_opts = build_common_opts(output_path)
        ydl_opts.update({
            'format': video_format,
            'merge_output_format': 'mp4',
        })
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url)
                filename = ydl.prepare_filename(info)
                base, _ = os.path.splitext(filename)
                return base + '.mp4'
        except DownloadError as exc:
            if 'Requested format is not available' in str(exc):
                last_format_error = exc
                continue
            raise

    if last_format_error:
        raise last_format_error

    raise DownloadError('Falha ao selecionar formato de vídeo.')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        tipo = request.form.get('tipo')
        max_height_raw = request.form.get('max_height')
        try:
            max_height = int(max_height_raw) if max_height_raw else None
        except (TypeError, ValueError):
            flash('Resolução inválida. Selecione um valor válido.')
            return redirect(url_for('index'))
        if not url or tipo not in ['mp3', 'mp4']:
            flash('Preencha todos os campos corretamente!')
            return redirect(url_for('index'))
        try:
            if tipo == 'mp3':
                file_path = download_youtube_audio(url, DOWNLOAD_FOLDER)
            else:
                file_path = download_youtube_video(url, DOWNLOAD_FOLDER, max_height)
            file_id = str(uuid.uuid4())
            new_name = os.path.join(DOWNLOAD_FOLDER, file_id + os.path.splitext(file_path)[1])
            os.rename(file_path, new_name)
            session['download_url'] = url_for('download', file_id=file_id, ext=os.path.splitext(file_path)[1][1:])
            return redirect(url_for('index'))
        except DownloadError as exc:
            message = str(exc)
            if "Sign in to confirm you’re not a bot" in message:
                flash(
                    'Erro do YouTube: bloqueio anti-bot detectado. '
                    'Adicione cookies.txt na pasta do projeto e tente novamente.'
                )
            elif "This video is not available" in message:
                flash(
                    'Erro do YouTube: vídeo indisponível para extração neste contexto. '
                    'Se abrir no navegador, tente novamente com cookies.txt.'
                )
            else:
                flash(f'Erro no download: {message}')
            return redirect(url_for('index'))
        except Exception as exc:
            flash(f'Erro inesperado: {exc}')
            return redirect(url_for('index'))
    download_url = session.pop('download_url', None)
    return render_template('index.html', download_url=download_url)

@app.route('/download/<file_id>.<ext>')
def download(file_id, ext):
    file_path = os.path.join(DOWNLOAD_FOLDER, f'{file_id}.{ext}')
    if not os.path.exists(file_path):
        flash('Arquivo não encontrado ou já baixado.')
        return redirect(url_for('index'))
    @after_this_request
    def remove_file(response):
        try:
            os.remove(file_path)
        except Exception:
            pass
        return response
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
