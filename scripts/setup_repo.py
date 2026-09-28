#!/usr/bin/env python3
"""
setup_repo.py
=============
Master setup and initialization script for the Computer Vision notes repository.

Automates:
1. Downloading canonical textbooks from verified URLs (with SSL tolerance & progress bar).
2. Processing textbooks into structured, hierarchical Markdown + extracted images.
3. Ingesting Quarto/Markdown repositories (e.g. Torralba et al.).
4. Building the local LanceDB multilingual vector database (RAG).
5. Running a self-diagnostic search query.

Usage:
    uv run --with pymupdf,pymupdf4llm,lancedb,fastembed,pyyaml python3 scripts/setup_repo.py [OPTIONS]

Options:
    --force             Re-download and re-process everything
    --skip-download     Skip downloading PDFs (process existing ones only)
    --skip-rag          Skip vector database indexing
"""

import os
import sys
import ssl
import json
import argparse
import subprocess
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = Path(__file__).resolve().parent / "books_config.json"
TEXTBOOK_DIR = BASE_DIR / "docs_clase" / "textBook"
SKILL_DIR = BASE_DIR / ".agents" / "skills" / "vc-textbook-rag"


def download_file(url: str, dest_path: Path):
    """Downloads a file with a progress bar and SSL tolerance."""
    print(f"⬇️ Descargando: {dest_path.name}")
    print(f"   URL: {url}")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        total_size = int(resp.headers.get("Content-Length", 0))
        block_size = 1024 * 1024  # 1 MB
        downloaded = 0

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, "wb") as f:
            while True:
                buffer = resp.read(block_size)
                if not buffer:
                    break
                downloaded += len(buffer)
                f.write(buffer)
                if total_size > 0:
                    percent = downloaded / total_size * 100
                    mb_down = downloaded / (1024 * 1024)
                    mb_tot = total_size / (1024 * 1024)
                    print(f"   Progreso: {percent:.1f}% ({mb_down:.1f} MB / {mb_tot:.1f} MB)", end="\r")
                else:
                    mb_down = downloaded / (1024 * 1024)
                    print(f"   Descargados: {mb_down:.1f} MB...", end="\r")

    print(f"\n✓ Descarga finalizada: {dest_path.name}")


def main():
    parser = argparse.ArgumentParser(description="Inicializa el entorno, descarga libros y construye el RAG.")
    parser.add_argument("--force", action="store_true", help="Re-descargar y re-procesar todo")
    parser.add_argument("--skip-download", action="store_true", help="Omitir descargas")
    parser.add_argument("--skip-rag", action="store_true", help="Omitir indexación vectorial")
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("🚀 INICIALIZACIÓN DEL REPOSITORIO DE VISIÓN POR COMPUTADOR")
    print("=" * 70)

    if not CONFIG_PATH.exists():
        print(f"❌ Error: Configuración no encontrada en {CONFIG_PATH}")
        sys.exit(1)

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    books = config.get("books", [])
    TEXTBOOK_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Download missing PDFs
    if not args.skip_download:
        print("\n[Paso 1/4] Comprobación y descarga de libros canónicos...")
        for b in books:
            if b.get("type") == "pdf":
                filename = b.get("filename")
                dest = TEXTBOOK_DIR / filename
                legacy_aliases = []
                if b["id"] == "szeliski":
                    legacy_aliases.append(TEXTBOOK_DIR / "textbook.pdf")
                elif b["id"] == "forsyth":
                    legacy_aliases.append(TEXTBOOK_DIR / "COMPUTER VISION A MODERN APPROACH.pdf")

                already_exists = dest.exists() or any(a.exists() for a in legacy_aliases)

                if already_exists and not args.force:
                    print(f"⏩ Ya disponible en local: {b['title']} ({filename})")
                else:
                    url = b.get("url")
                    if url:
                        try:
                            download_file(url, dest)
                        except Exception as e:
                            print(f"❌ Error descargando {b['title']}: {e}")
                    else:
                        print(f"⚠️ Sin URL de descarga directa para: {b['title']}")

    # 2. Process Textbooks into Modular Markdown
    print("\n[Paso 2/4] Procesando libros a Markdown modular...")
    cmd_proc = [
        sys.executable,
        str(BASE_DIR / "scripts" / "process_textbooks.py")
    ]
    if args.force:
        cmd_proc.append("--force")
    res_proc = subprocess.run(cmd_proc)
    if res_proc.returncode != 0:
        print("⚠️ Advertencia: Algunos libros tuvieron errores en el procesamiento.")

    # 3. Build RAG Vector Index
    if not args.skip_rag:
        print("\n[Paso 3/4] Construyendo índice vectorial local de LanceDB...")
        cmd_rag = [
            sys.executable,
            str(SKILL_DIR / "scripts" / "build_index.py"),
            "--force"
        ]
        res_rag = subprocess.run(cmd_rag)
        if res_rag.returncode != 0:
            print("⚠️ Error construyendo el índice vectorial.")
    else:
        print("\n⏩ Paso 3/4 omitido (--skip-rag).")

    # 4. Self-test query
    print("\n[Paso 4/4] Ejecutando consulta de autodiagnóstico...")
    cmd_test = [
        sys.executable,
        str(SKILL_DIR / "scripts" / "query.py"),
        "geometria epipolar matriz fundamental",
        "--top-k", "1",
        "--json"
    ]
    try:
        test_out = subprocess.run(cmd_test, capture_output=True, text=True)
        if test_out.returncode == 0:
            print("✓ Diagnóstico completado: El sistema RAG responde correctamente.")
        else:
            print("⚠️ El diagnóstico devolvió un aviso:", test_out.stderr)
    except Exception as e:
        print("⚠️ No se pudo ejecutar el test de diagnóstico:", e)

    print("\n" + "=" * 70)
    print("🎉 ¡TODO LISTO! El repositorio está completamente configurado.")
    print("   - Abre la carpeta en Obsidian para navegar por los temas y textbooks.")
    print("   - Ejecuta búsquedas semánticas con: uv run python3 .agents/skills/vc-textbook-rag/scripts/query.py \"<duda>\"")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
