from flask import Flask, render_template, request, send_file, redirect, url_for, after_this_request, flash, session
import os
import yt_dlp
import uuid

app = Flask(__name__)
app.secret_key = 'supersecretkey'
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Funções de download

def download_youtube_audio(video_url, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{output_path}/%(title)s_%(id)s.%(ext)s',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    cookies_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')
    if os.path.exists(cookies_path):
        ydl_opts['cookies'] = cookies_path
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url)
        filename = ydl.prepare_filename(info)
        base, _ = os.path.splitext(filename)
        return base + '.mp3'

def download_youtube_video(video_url, output_path):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': f'{output_path}/%(title)s_%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    cookies_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')
    if os.path.exists(cookies_path):
        ydl_opts['cookies'] = cookies_path
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url)
        filename = ydl.prepare_filename(info)
        base, _ = os.path.splitext(filename)
        return base + '.mp4'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        tipo = request.form.get('tipo')
        if not url or tipo not in ['mp3', 'mp4']:
            flash('Preencha todos os campos corretamente!')
            return redirect(url_for('index'))
        try:
            if tipo == 'mp3':
                file_path = download_youtube_audio(url, DOWNLOAD_FOLDER)
            else:
                file_path = download_youtube_video(url, DOWNLOAD_FOLDER)
            file_id = str(uuid.uuid4())
            new_name = os.path.join(DOWNLOAD_FOLDER, file_id + os.path.splitext(file_path)[1])
            os.rename(file_path, new_name)
            session['download_url'] = url_for('download', file_id=file_id, ext=os.path.splitext(file_path)[1][1:])
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Erro: {e}')
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
