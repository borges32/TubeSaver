import os
import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar

# Função para escolher o diretório de destino
def choose_directory():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_destino.delete(0, tk.END)
        entry_destino.insert(0, folder_selected)

# Função para atualizar a barra de progresso
def progress_hook(d):
    if d['status'] == 'downloading':
        p = d['_percent_str']
        progress['value'] = float(p.replace('%', ''))
        root.update_idletasks()


def download_youtube_audio(audio_url, output_path):
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
        try:
            ydl.download([audio_url])
            messagebox.showinfo("Sucesso", "baixado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao baixar: {str(e)}")

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
        try:
            ydl.download([video_url])
            messagebox.showinfo("Sucesso", "baixado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao baixar: {str(e)}")
        

# Função para fazer o download do vídeo/áudio
def download():
    url = entry_url.get()
    destination = entry_destino.get()
    download_type = var_download_type.get()

    if not url or not destination:
        messagebox.showwarning("Erro", "Por favor, insira uma URL e escolha um diretório de destino.")
        return


    if download_type == 'MP3':
        download_youtube_audio(url, destination)
    else:
        download_youtube_video(url, destination)

    ydl_opts = {
        'format': 'bestaudio/best' if download_type == 'MP3' else 'bestvideo+bestaudio',
        'outtmpl': os.path.join(destination, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if download_type == 'MP3' else []
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            messagebox.showinfo("Sucesso", f"{download_type} baixado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao baixar: {str(e)}")

# Criar a interface gráfica
root = tk.Tk()
root.title("Downloader de Vídeo e Áudio (YouTube)")

# Widgets da interface
label_url = tk.Label(root, text="URL do vídeo:")
label_url.grid(row=0, column=0, padx=5, pady=5)

entry_url = tk.Entry(root, width=100)
entry_url.grid(row=0, column=1, padx=5, pady=5)

label_destino = tk.Label(root, text="Destino:")
label_destino.grid(row=1, column=0, padx=5, pady=5)

entry_destino = tk.Entry(root, width=100)
entry_destino.grid(row=1, column=1, padx=5, pady=5)

btn_destino = tk.Button(root, text="Escolher...", command=choose_directory)
btn_destino.grid(row=1, column=2, padx=5, pady=5)

# Tipo de download (MP3 ou MP4)
var_download_type = tk.StringVar(value='MP4')
radio_mp4 = tk.Radiobutton(root, text="MP4", variable=var_download_type, value="MP4")
radio_mp4.grid(row=2, column=0, padx=5, pady=5)

radio_mp3 = tk.Radiobutton(root, text="MP3", variable=var_download_type, value="MP3")
radio_mp3.grid(row=2, column=1, padx=5, pady=5)

# Barra de progresso
progress = Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress.grid(row=3, column=0, columnspan=3, padx=5, pady=10)

# Botão de download
btn_download = tk.Button(root, text="Baixar", command=download)
btn_download.grid(row=4, column=0, columnspan=3, padx=5, pady=10)

# Iniciar a aplicação
root.mainloop()
