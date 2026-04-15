#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Executa downloads em lote usando URLs de um arquivo texto."
    )
    parser.add_argument(
        "--lista",
        default="listavideos.txt",
        help="Arquivo com uma URL por linha (padrão: listavideos.txt).",
    )
    return parser.parse_args()


def resolve_list_file(preferred_name: str) -> Path:
    preferred = Path(preferred_name)
    if preferred.exists():
        return preferred

    fallback = Path("listaVideos.txt")
    if fallback.exists():
        return fallback

    raise FileNotFoundError(
        f"Arquivo de lista não encontrado: '{preferred_name}' "
        "nem 'listaVideos.txt'."
    )


def iter_urls(file_path: Path):
    for line in file_path.read_text(encoding="utf-8").splitlines():
        url = line.strip()
        if not url or url.startswith("#"):
            continue
        yield url


def main():
    args = parse_args()

    try:
        list_file = resolve_list_file(args.lista)
    except FileNotFoundError as exc:
        print(exc)
        return 1

    urls = list(iter_urls(list_file))
    if not urls:
        print(f"Nenhuma URL válida encontrada em: {list_file}")
        return 1

    print(f"Lendo URLs de: {list_file}")
    print(f"Total de itens: {len(urls)}")

    success = 0
    failed = 0
    py = sys.executable

    for index, url in enumerate(urls, start=1):
        cmd = [py, "app.py", url, "mp4", "--max-height", "1440"]
        print(f"\n[{index}/{len(urls)}] Executando: {' '.join(cmd)}")
        result = subprocess.run(cmd)

        if result.returncode == 0:
            success += 1
            print(f"[{index}] OK")
        else:
            failed += 1
            print(f"[{index}] Falhou (exit code: {result.returncode})")

    print("\nResumo:")
    print(f"- Sucesso: {success}")
    print(f"- Falhas: {failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
