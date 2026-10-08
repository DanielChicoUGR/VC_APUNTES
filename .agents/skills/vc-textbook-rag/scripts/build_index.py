#!/usr/bin/env python3
"""
build_index.py
==============
Indexes textbook Markdown files (and class documents) into a local LanceDB vector database.
Uses FastEmbed (ONNX, multilingual, CPU-friendly) to generate dense vector embeddings.

Usage:
    uv run --with lancedb,fastembed,pyyaml python3 .agents/skills/vc-textbook-rag/scripts/build_index.py [OPTIONS]

Options:
    --force             Re-index everything from scratch (overwrite table)
    --batch-size N      Embedding batch size (default: 64)
    --fts-only          Add/update BM25 without recomputing vectors
"""

import os
import sys
import re
import argparse
from pathlib import Path

try:
    import yaml
    import lancedb
    from lancedb.index import FTS
except ImportError:
    print("Error: Missing required packages. Run with:")
    print("uv run --with lancedb,fastembed,pyyaml python3 .agents/skills/vc-textbook-rag/scripts/build_index.py")
    sys.exit(1)

# Default paths relative to workspace root
WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
SKILL_DIR = Path(__file__).resolve().parents[1]
DB_DIR = SKILL_DIR / "data" / "lancedb"
DOCS_DIR = WORKSPACE_ROOT / "docs_clase"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def parse_markdown_file(file_path: Path):
    """
    Parses a markdown file, extracts YAML frontmatter, and splits content by headings.
    Returns a list of chunk dicts.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

    # 1. Extract Frontmatter
    frontmatter = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
            except Exception:
                frontmatter = {}
            body = parts[2]

    book_name = frontmatter.get("book", "")
    if not book_name:
        if "Szeliski" in str(file_path):
            book_name = "Szeliski"
        elif "Forsyth" in str(file_path):
            book_name = "Forsyth & Ponce"
        else:
            book_name = "Docs Clase"

    chapter_title = frontmatter.get("chapter_title", file_path.parent.name)
    section_title = frontmatter.get("section_title", file_path.stem)
    pages_pdf = frontmatter.get("pages_pdf", [])
    pages_str = f"{pages_pdf[0]}-{pages_pdf[1]}" if len(pages_pdf) == 2 else ""

    # 2. Split body into heading-based sections
    lines = body.splitlines()
    chunks = []
    current_heading = section_title
    current_lines = []

    def flush_chunk():
        nonlocal current_lines, current_heading
        text_block = "\n".join(current_lines).strip()
        current_lines = []
        if not text_block:
            return

        # Skip navigation bars, pure image references without context, or tiny blocks
        clean_text = re.sub(r'\[←.*?\]\(.*?\)', '', text_block)
        clean_text = re.sub(r'\[↑.*?\]\(.*?\)', '', clean_text)
        clean_text = re.sub(r'\[.*?→\]\(.*?\)', '', clean_text)
        clean_text = clean_text.strip()
        if len(clean_text) < 40:
            return

        # Construct contextualized text for embedding
        header_context = f"[Libro: {book_name} | Capítulo: {chapter_title} | Sección: {section_title} | Tema: {current_heading}]"
        embed_text = f"{header_context}\n{clean_text}"

        chunks.append({
            "book": str(book_name),
            "chapter": str(chapter_title),
            "section": str(section_title),
            "heading": str(current_heading),
            "pages_pdf": str(pages_str),
            "file_path": str(file_path.relative_to(WORKSPACE_ROOT)),
            "text": clean_text,
            "embed_text": embed_text
        })

    for line in lines:
        if line.startswith(("## ", "### ")):
            flush_chunk()
            current_heading = line.lstrip("#").strip()
        else:
            current_lines.append(line)

    flush_chunk()
    return chunks


def collect_markdown_documents():
    """Finds all markdown files to index under docs_clase/, explicitly skipping personal Tema folders."""
    docs = []
    if not DOCS_DIR.exists():
        print(f"Warning: {DOCS_DIR} not found.")
        return docs

    for path in DOCS_DIR.rglob("*.md"):
        # Skip index files and metadata files that are pure lists
        if path.name in ("_INDEX.md", "README.md") or "_METADATA" in path.name:
            continue
        docs.append(path)

    return sorted(docs)


def main():
    parser = argparse.ArgumentParser(description="Index textbook documents into LanceDB.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing vector database")
    parser.add_argument("--fts-only", action="store_true", help="Prepare BM25 on existing table without embeddings")
    parser.add_argument("--batch-size", type=int, default=64, help="Embedding batch size")
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error("--batch-size must be positive")
    if args.fts_only:
        table = lancedb.connect(str(DB_DIR)).open_table("textbook_chunks")
        table.create_index("text", config=FTS(), replace=True)
        print("BM25 index ready; existing vectors unchanged.")
        return
    if DB_DIR.exists() and not args.force:
        db = lancedb.connect(str(DB_DIR))
        try:
            db.open_table("textbook_chunks")
        except ValueError:
            pass
        else:
            parser.error("Index already exists. Use --force to rebuild or --fts-only for BM25.")

    from fastembed import TextEmbedding

    print("=======================================================")
    print("🚀 VC Textbook RAG - Indexador Vectorial Local")
    print(f"   Modelo: {MODEL_NAME}")
    print(f"   Base de datos: {DB_DIR}")
    print("=======================================================")

    md_files = collect_markdown_documents()
    print(f"📁 Encontrados {len(md_files)} archivos Markdown en {DOCS_DIR.relative_to(WORKSPACE_ROOT)}")

    all_chunks = []
    for f in md_files:
        chunks = parse_markdown_file(f)
        all_chunks.extend(chunks)

    print(f"🧩 Generados {len(all_chunks)} fragmentos semánticos con contexto.")

    if not all_chunks:
        print("❌ No se encontraron fragmentos para indexar.")
        return

    # Add unique IDs
    for idx, c in enumerate(all_chunks):
        c["id"] = f"chunk_{idx:05d}"

    print(f"🧠 Inicializando modelo FastEmbed: {MODEL_NAME}...")
    model = TextEmbedding(MODEL_NAME)

    print(f"⚡ Calculando embeddings para {len(all_chunks)} chunks (batch size: {args.batch_size})...")
    texts_to_embed = [c["embed_text"] for c in all_chunks]

    embeddings = []
    total = len(texts_to_embed)
    for i in range(0, total, args.batch_size):
        batch = texts_to_embed[i:i + args.batch_size]
        batch_embs = list(model.embed(batch))
        embeddings.extend(batch_embs)
        print(f"   Progreso: [{min(i + args.batch_size, total)}/{total}] embeddings calculados...", end="\r")

    print(f"\n✓ Embeddings calculados con éxito.")

    # Assign vectors to records (drop temporary embed_text from storage to save space)
    records = []
    for c, emb in zip(all_chunks, embeddings):
        records.append({
            "id": c["id"],
            "book": c["book"],
            "chapter": c["chapter"],
            "section": c["section"],
            "heading": c["heading"],
            "pages_pdf": c["pages_pdf"],
            "file_path": c["file_path"],
            "text": c["text"],
            "vector": emb
        })

    # Save into LanceDB
    DB_DIR.mkdir(parents=True, exist_ok=True)
    db = lancedb.connect(str(DB_DIR))
    table_name = "textbook_chunks"

    print(f"💾 Guardando tabla '{table_name}' en LanceDB: {DB_DIR}...")
    table = db.create_table(table_name, data=records, mode="overwrite")
    table.create_index("text", config=FTS(), replace=True)
    print(f"✓ Éxito: {table.count_rows()} fragmentos indexados con vectores y BM25.")
    print("=======================================================")


if __name__ == "__main__":
    main()
