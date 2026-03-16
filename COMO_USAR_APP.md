# TubeSaver - Como Usar (CLI)

Ferramenta de linha de comando para baixar vídeos e áudios do YouTube e converter arquivos MP4 para MP3.

## Pré-requisitos

- **Python 3** instalado
- **ffmpeg** instalado (necessário para conversão de áudio e merge de vídeo+áudio)
- **Node.js** ou **Deno** (opcional, melhora a extração de alguns vídeos)

## Instalação

```bash
# Crie e ative um ambiente virtual (recomendado)
python3 -m venv myenv_tube
source myenv_tube/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

## Uso

```bash
python app.py <URL_ou_CAMINHO> <tipo> [--output DIRETORIO] [--max-height ALTURA]
```

### Argumentos

| Argumento       | Descrição                                                      |
|-----------------|----------------------------------------------------------------|
| `url`           | URL do vídeo no YouTube ou caminho de um arquivo MP4 local     |
| `tipo`          | Modo de operação: `mp3`, `mp4`, `mp4mp3` ou `list`            |
| `--output`      | Diretório de saída (padrão: diretório atual `./`)              |
| `--max-height`  | Altura máxima do vídeo em pixels (ex.: 720, 1080, 1440, 2160) |

### Modos de operação

#### `mp3` - Baixar apenas o áudio

Baixa o áudio do vídeo do YouTube e converte para MP3 (192 kbps).

```bash
python app.py "https://www.youtube.com/watch?v=EXEMPLO" mp3
python app.py "https://www.youtube.com/watch?v=EXEMPLO" mp3 --output ~/Musicas
```

#### `mp4` - Baixar o vídeo

Baixa o vídeo com a melhor qualidade disponível em formato MP4. Use `--max-height` para limitar a resolução.

```bash
# Melhor qualidade disponível
python app.py "https://www.youtube.com/watch?v=EXEMPLO" mp4

# Limitar a 1080p
python app.py "https://www.youtube.com/watch?v=EXEMPLO" mp4 --max-height 1080

# Salvar em pasta específica
python app.py "https://www.youtube.com/watch?v=EXEMPLO" mp4 --output ~/Videos --max-height 720
```

#### `mp4mp3` - Converter arquivo MP4 local para MP3

Converte um arquivo MP4 já existente no seu computador para MP3 (192 kbps, 44100 Hz).

```bash
python app.py /caminho/para/video.mp4 mp4mp3
python app.py /caminho/para/video.mp4 mp4mp3 --output ~/Musicas
```

#### `list` - Listar formatos disponíveis

Exibe todos os formatos de download disponíveis para um vídeo (sem baixar nada).

```bash
python app.py "https://www.youtube.com/watch?v=EXEMPLO" list
```

## Cookies (opcional)

Se o YouTube bloquear o download com erro anti-bot, exporte os cookies do seu navegador para um arquivo `cookies.txt` na raiz do projeto. O app detecta e usa esse arquivo automaticamente.

## Solução de problemas

| Erro                                        | Solução                                                        |
|---------------------------------------------|----------------------------------------------------------------|
| `Sign in to confirm you're not a bot`       | Adicione um arquivo `cookies.txt` na raiz do projeto           |
| `This video is not available`               | Verifique a URL; tente adicionar `cookies.txt`                 |
| `Erro ao converter com ffmpeg`              | Instale o ffmpeg: `sudo apt install ffmpeg`                    |
| `Dependência ausente`                       | Execute `pip install -r requirements.txt`                      |
