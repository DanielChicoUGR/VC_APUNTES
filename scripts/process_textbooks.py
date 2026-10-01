#!/usr/bin/env python3
"""
process_textbooks.py
====================
Extracts and structures textbook PDFs and Quarto repositories into a modular,
hierarchical Markdown format optimized for Obsidian vaults and selective LLM agent retrieval.

Reads book definitions from `scripts/books_config.json`.

Usage:
    uv run --with pymupdf,pymupdf4llm,pyyaml python3 scripts/process_textbooks.py [OPTIONS]

Options:
    --book ID           Process only a specific book by ID (e.g. szeliski, forsyth, hartley_zisserman, etc.)
    --chapter N         Process only chapter N (for fast testing/incremental)
    --force             Overwrite existing files
    --no-images         Skip extracting images
"""

import os
import sys
import re
import io
import json
import zipfile
import argparse
import unicodedata
import urllib.request
from pathlib import Path

try:
    import pymupdf
    import pymupdf4llm
    import yaml
except ImportError:
    print("Error: Required libraries not found. Run with:")
    print("uv run --with pymupdf,pymupdf4llm,pyyaml python3 scripts/process_textbooks.py")
    sys.exit(1)

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = Path(__file__).resolve().parent / "books_config.json"
TEXTBOOK_DIR = BASE_DIR / "docs_clase" / "textBook"


def slugify(text: str) -> str:
    """Normalize and slugify a title for filenames and directories."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r'[^\w\s\.-]', '_', text)
    text = re.sub(r'\s+', '_', text.strip())
    text = re.sub(r'_+', '_', text)
    return text.strip('_')


def clean_math_and_links(text: str, current_file_path: Path, section_map: dict, chapter_map: dict) -> str:
    """Auto-link mentions of 'Section X.Y' and 'Chapter X' to their relative markdown paths."""
    current_dir = current_file_path.parent

    def replace_section(match):
        full_match = match.group(0)
        sec_num = match.group(1)
        if sec_num in section_map:
            target_path = section_map[sec_num]
            rel_path = os.path.relpath(target_path, current_dir)
            return f"[{full_match}]({rel_path})"
        return full_match

    def replace_chapter(match):
        full_match = match.group(0)
        chap_num = match.group(1)
        if chap_num in chapter_map:
            target_path = chapter_map[chap_num]
            rel_path = os.path.relpath(target_path, current_dir)
            return f"[{full_match}]({rel_path})"
        return full_match

    text = re.sub(r'(?<!\[)(?:Section|Sec\.)\s+(\d+\.\d+)(?!\])', replace_section, text)
    text = re.sub(r'(?<!\[)Chapter\s+(\d+)(?!\])', replace_chapter, text)
    return text


def parse_generic_toc(doc: pymupdf.Document) -> list:
    """Generic hierarchical Table of Contents parser for standard textbooks."""
    toc = doc.get_toc()
    total_pages = len(doc)
    if not toc:
        return [{
            'title': 'Documento Completo',
            'start_page': 1,
            'end_page': total_pages,
            'toc_index': 0,
            'sections': []
        }]

    min_lvl = min(item[0] for item in toc)
    chapters = []

    for i, item in enumerate(toc):
        lvl, title, page = item[:3]
        if lvl == min_lvl:
            chapters.append({
                'title': title.strip(),
                'start_page': max(1, page),
                'toc_index': i,
                'sections': []
            })

    for i in range(len(chapters)):
        next_page = chapters[i + 1]['start_page'] if i + 1 < len(chapters) else total_pages + 1
        chapters[i]['end_page'] = max(chapters[i]['start_page'], next_page - 1)

    for chap in chapters:
        c_idx = chap['toc_index']
        next_c_idx = len(toc)
        for other in chapters:
            if other['toc_index'] > c_idx:
                next_c_idx = min(next_c_idx, other['toc_index'])
                break

        for idx in range(c_idx + 1, next_c_idx):
            lvl, title, page = toc[idx][:3]
            if lvl == min_lvl + 1:
                chap['sections'].append({
                    'title': title.strip(),
                    'start_page': max(chap['start_page'], page)
                })

        for s_idx in range(len(chap['sections'])):
            next_spage = (chap['sections'][s_idx + 1]['start_page']
                          if s_idx + 1 < len(chap['sections'])
                          else chap['end_page'] + 1)
            chap['sections'][s_idx]['end_page'] = max(chap['sections'][s_idx]['start_page'], next_spage - 1)

    return chapters


def parse_szeliski_toc(doc: pymupdf.Document) -> list:
    """Specialized Table of Contents for Szeliski."""
    toc = doc.get_toc()
    total_pages = len(doc)
    chapters = []
    for i, item in enumerate(toc):
        lvl, title, page = item[:3]
        if lvl == 1:
            chapters.append({'title': title.strip(), 'start_page': page, 'toc_index': i, 'sections': []})

    for i in range(len(chapters)):
        next_page = chapters[i + 1]['start_page'] if i + 1 < len(chapters) else total_pages + 1
        chapters[i]['end_page'] = next_page - 1

    for chap in chapters:
        c_idx = chap['toc_index']
        next_c_idx = len(toc)
        for other in chapters:
            if other['toc_index'] > c_idx:
                next_c_idx = min(next_c_idx, other['toc_index'])
                break
        for idx in range(c_idx + 1, next_c_idx):
            lvl, title, page = toc[idx][:3]
            if lvl == 2:
                chap['sections'].append({'title': title.strip(), 'start_page': page})
        for s_idx in range(len(chap['sections'])):
            next_spage = (chap['sections'][s_idx + 1]['start_page']
                          if s_idx + 1 < len(chap['sections'])
                          else chap['end_page'] + 1)
            chap['sections'][s_idx]['end_page'] = next_spage - 1
    return chapters


def parse_forsyth_toc(doc: pymupdf.Document) -> list:
    """Specialized Table of Contents for Forsyth & Ponce."""
    toc = doc.get_toc()
    total_pages = len(doc)
    chapters = []
    for i, item in enumerate(toc):
        lvl, title, page = item[:3]
        title_str = title.strip()
        is_chap = ((lvl == 2 and re.match(r'^\d+\s', title_str)) or
                   (lvl == 1 and not title_str.startswith(('I:', 'II:', 'III:', 'IV:', 'V:', 'VI:', 'VII:',
                                                          'Cover', '©', 'Dedication', 'Contents'))))
        if is_chap:
            chapters.append({'title': title_str, 'start_page': page, 'toc_index': i, 'sections': []})

    for i in range(len(chapters)):
        next_page = chapters[i + 1]['start_page'] if i + 1 < len(chapters) else total_pages + 1
        chapters[i]['end_page'] = next_page - 1

    for chap in chapters:
        c_idx = chap['toc_index']
        next_c_idx = len(toc)
        for other in chapters:
            if other['toc_index'] > c_idx:
                next_c_idx = min(next_c_idx, other['toc_index'])
                break
        for idx in range(c_idx + 1, next_c_idx):
            lvl, title, page = toc[idx][:3]
            if lvl == 3 or (lvl == 2 and not re.match(r'^\d+\s', title.strip())):
                chap['sections'].append({'title': title.strip(), 'start_page': page})
        for s_idx in range(len(chap['sections'])):
            next_spage = (chap['sections'][s_idx + 1]['start_page']
                          if s_idx + 1 < len(chap['sections'])
                          else chap['end_page'] + 1)
            chap['sections'][s_idx]['end_page'] = next_spage - 1
    return chapters


def build_navigation_maps(chapters: list, out_dir: Path):
    section_map = {}
    chapter_map = {}
    pages_to_file = {}

    for c_idx, chap in enumerate(chapters):
        c_title = chap['title']
        chap_num_match = re.search(r'(?:Chapter\s+|^\b)(\d+)', c_title, re.IGNORECASE)
        chap_num = chap_num_match.group(1) if chap_num_match else str(c_idx + 1)
        chap_slug = slugify(c_title)
        chap_dir = out_dir / chap_slug
        overview_path = chap_dir / "00_Overview.md"

        chapter_map[chap_num] = overview_path
        for p in range(chap['start_page'], chap['end_page'] + 1):
            pages_to_file[p] = str(overview_path.relative_to(out_dir))

        for sec in chap['sections']:
            s_title = sec['title']
            sec_num_match = re.match(r'^(\d+\.\d+)', s_title)
            sec_num = sec_num_match.group(1) if sec_num_match else None
            sec_slug = slugify(s_title)
            sec_path = chap_dir / f"{sec_slug}.md"

            if sec_num:
                section_map[sec_num] = sec_path
            for p in range(sec['start_page'], sec['end_page'] + 1):
                pages_to_file[p] = str(sec_path.relative_to(out_dir))

    return section_map, chapter_map, pages_to_file


def process_pdf_book(book: dict, target_chapter=None, force=False, extract_images=True):
    pdf_filename = book.get("filename")
    pdf_path = TEXTBOOK_DIR / pdf_filename

    # Fallback to legacy names if present
    if not pdf_path.exists():
        if book["id"] == "szeliski" and (TEXTBOOK_DIR / "textbook.pdf").exists():
            pdf_path = TEXTBOOK_DIR / "textbook.pdf"
        elif book["id"] == "forsyth" and (TEXTBOOK_DIR / "COMPUTER VISION A MODERN APPROACH.pdf").exists():
            pdf_path = TEXTBOOK_DIR / "COMPUTER VISION A MODERN APPROACH.pdf"

    out_dir = TEXTBOOK_DIR / book["folder"]
    book_name = book["title"]
    author = book["author"]
    parser_type = book.get("parser", "generic")

    print("\n=======================================================")
    print(f"📖 Procesando PDF: {book_name} ({author})")
    print(f"   Archivo: {pdf_path.name}")
    print(f"   Destino: {out_dir}")
    print("=======================================================")

    if not pdf_path.exists():
        print(f"⚠️ Aviso: Archivo PDF no encontrado: {pdf_path}. Omitiendo hasta su descarga.")
        return

    doc = pymupdf.open(str(pdf_path))
    total_pages = len(doc)
    print(f"📄 Páginas totales: {total_pages}")

    if parser_type == "szeliski":
        chapters = parse_szeliski_toc(doc)
    elif parser_type == "forsyth":
        chapters = parse_forsyth_toc(doc)
    else:
        chapters = parse_generic_toc(doc)

    print(f"📑 Detectados {len(chapters)} capítulos/secciones principales.")
    out_dir.mkdir(parents=True, exist_ok=True)

    section_map, chapter_map, pages_to_file = build_navigation_maps(chapters, out_dir)

    # Save metadata JSON
    metadata_file = out_dir / "_METADATA.json"
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump({
            "book": book_name,
            "author": author,
            "total_pages": total_pages,
            "pages_to_file": pages_to_file,
            "chapters": [{
                "title": c['title'],
                "pages": [c['start_page'], c['end_page']],
                "sections": [{
                    "title": s['title'],
                    "pages": [s['start_page'], s['end_page']]
                } for s in c['sections']]
            } for c in chapters]
        }, f, indent=2, ensure_ascii=False)

    for c_idx, chap in enumerate(chapters):
        c_title = chap['title']
        chap_num_match = re.search(r'(?:Chapter\s+|^\b)(\d+)', c_title, re.IGNORECASE)
        chap_num_str = chap_num_match.group(1) if chap_num_match else str(c_idx + 1)

        if target_chapter is not None and str(target_chapter) != chap_num_str:
            continue

        chap_slug = slugify(c_title)
        chap_dir = out_dir / chap_slug
        img_dir = chap_dir / "images"

        chap_dir.mkdir(parents=True, exist_ok=True)
        if extract_images:
            img_dir.mkdir(parents=True, exist_ok=True)

        overview_path = chap_dir / "00_Overview.md"
        print(f"\n📂 [{c_idx + 1}/{len(chapters)}] {c_title} (pp. {chap['start_page']}-{chap['end_page']})")

        # Overview
        if not overview_path.exists() or force:
            overview_lines = [
                "---",
                f'book: "{book_name}"',
                f'author: "{author}"',
                f'chapter_title: "{c_title}"',
                f'pages_pdf: [{chap["start_page"]}, {chap["end_page"]}]',
                "type: chapter_overview",
                "---\n",
                f"# {c_title}\n",
                f"> **Libro:** {book_name}  ",
                f"> **Autor:** {author}  ",
                f"> **Páginas en PDF:** {chap['start_page']} - {chap['end_page']}  ",
                "> **Navegación:** [Índice General](../_INDEX.md)\n",
                "## Secciones del Capítulo\n",
            ]

            if chap['sections']:
                for s in chap['sections']:
                    s_slug = slugify(s['title'])
                    s_filename = f"{s_slug}.md"
                    overview_lines.append(f"- [{s['title']}](./{s_filename}) *(págs. {s['start_page']}-{s['end_page']})*")
            else:
                overview_lines.append("*(Capítulo sin subsecciones; contenido en el archivo principal).*")

            intro_end_page = chap['sections'][0]['start_page'] - 1 if chap['sections'] else chap['end_page']
            if intro_end_page >= chap['start_page']:
                overview_lines.append("\n---\n## Introducción y Resumen Conceptual\n")
                intro_pages = list(range(chap['start_page'] - 1, min(intro_end_page, chap['start_page'] + 2)))
                try:
                    intro_md = pymupdf4llm.to_markdown(
                        doc,
                        pages=intro_pages,
                        write_images=extract_images,
                        image_path=str(img_dir) if extract_images else ""
                    )
                    if extract_images:
                        intro_md = re.sub(r'!\[(.*?)\]\([^)]*images/([^)]+)\)', r'![\1](images/\2)', intro_md)
                    intro_md = clean_math_and_links(intro_md, overview_path, section_map, chapter_map)
                    overview_lines.append(intro_md)
                except Exception as e:
                    overview_lines.append(f"*(No se pudo extraer texto introductorio: {e})*")

            with open(overview_path, "w", encoding="utf-8") as f:
                f.write("\n".join(overview_lines))
            print("   ✓ Creado: 00_Overview.md")
        else:
            print("   ⏩ Omitido (ya existe): 00_Overview.md")

        # Sections
        for s_idx, sec in enumerate(chap['sections']):
            s_title = sec['title']
            s_slug = slugify(s_title)
            sec_path = chap_dir / f"{s_slug}.md"

            if sec_path.exists() and not force:
                continue

            start_p = max(0, sec['start_page'] - 1)
            end_p = max(start_p, sec['end_page'] - 1)
            page_range = list(range(start_p, end_p + 1))

            prev_sec = chap['sections'][s_idx - 1] if s_idx > 0 else None
            next_sec = chap['sections'][s_idx + 1] if s_idx + 1 < len(chap['sections']) else None

            nav_prev = f"[← {prev_sec['title']}](./{slugify(prev_sec['title'])}.md)" if prev_sec else "[← Inicio del Capítulo](./00_Overview.md)"
            nav_next = f"[{next_sec['title']} →](./{slugify(next_sec['title'])}.md)" if next_sec else "[Fin del Capítulo →](./00_Overview.md)"
            nav_bar = f"{nav_prev} | [↑ Resumen del Capítulo](./00_Overview.md) | {nav_next}"

            sec_lines = [
                "---",
                f'book: "{book_name}"',
                f'author: "{author}"',
                f'chapter_title: "{c_title}"',
                f'section_title: "{s_title}"',
                f'pages_pdf: [{sec["start_page"]}, {sec["end_page"]}]',
                "type: section_content",
                "---\n",
                f"{nav_bar}\n",
                f"# {s_title}\n",
                f"> **Páginas del libro:** {sec['start_page']} a {sec['end_page']}  ",
                f"> **Capítulo:** [{c_title}](./00_Overview.md)\n",
                "---\n"
            ]

            try:
                sec_md = pymupdf4llm.to_markdown(
                    doc,
                    pages=page_range,
                    write_images=extract_images,
                    image_path=str(img_dir) if extract_images else ""
                )
                if extract_images:
                    sec_md = re.sub(r'!\[(.*?)\]\([^)]*images/([^)]+)\)', r'![\1](images/\2)', sec_md)
                sec_md = clean_math_and_links(sec_md, sec_path, section_map, chapter_map)
                sec_lines.append(sec_md)
                sec_lines.append(f"\n\n---\n{nav_bar}\n")

                with open(sec_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(sec_lines))
                print(f"   ✓ Creado: {sec_path.name} (págs. {sec['start_page']}-{sec['end_page']})")
            except Exception as e:
                print(f"   ❌ Error en sección {s_title}: {e}")

    # Global _INDEX.md
    index_path = out_dir / "_INDEX.md"
    index_lines = [
        f"# Índice General: {book_name}",
        f"**Autor:** {author}  ",
        f"**Páginas totales:** {total_pages}\n",
        "> [!tip] Guía para el Agente y Búsqueda Rápida",
        "> - Utiliza este índice para localizar el capítulo o sección exacta antes de leer.",
        "> - Cada enlace conduce al resumen ligero (`00_Overview.md`) o a la sección específica.\n",
        "## Tabla de Contenidos Estructurada\n"
    ]
    for chap in chapters:
        chap_slug = slugify(chap['title'])
        overview_rel = f"{chap_slug}/00_Overview.md"
        index_lines.append(f"\n### [{chap['title']}]({overview_rel}) *(págs. {chap['start_page']}-{chap['end_page']})*")
        for sec in chap['sections']:
            sec_slug = slugify(sec['title'])
            sec_rel = f"{chap_slug}/{sec_slug}.md"
            index_lines.append(f"- [{sec['title']}]({sec_rel}) *(págs. {sec['start_page']}-{sec['end_page']})*")

    with open(index_path, "w", encoding="utf-8") as f:
        f.write("\n".join(index_lines))
    print(f"✓ Guardado: {index_path}")
    doc.close()


def process_quarto_repo(book: dict, force=False):
    """Processes a GitHub Quarto book repository (e.g. Torralba visionbook) by downloading .qmd files directly."""
    out_dir = TEXTBOOK_DIR / book["folder"]
    book_name = book["title"]
    author = book["author"]
    repo_name = "Foundations-of-Computer-Vision/visionbook"

    print("\n=======================================================")
    print(f"🌐 Procesando Repositorio Quarto/Markdown: {book_name}")
    print(f"   Repositorio GitHub: {repo_name}")
    print(f"   Destino: {out_dir}")
    print("=======================================================")

    if out_dir.exists() and not force and (out_dir / "_INDEX.md").exists():
        print(f"⏩ Omitido: {book_name} ya está procesado.")
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    img_dir = out_dir / "images"
    img_dir.mkdir(parents=True, exist_ok=True)

    print("🔍 Obteniendo lista de capítulos (.qmd) desde GitHub API...")
    tree_url = f"https://api.github.com/repos/{repo_name}/git/trees/main?recursive=1"
    req = urllib.request.Request(tree_url, headers={"User-Agent": "Mozilla/5.0"})
    
    qmd_files = []
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            tree_data = json.loads(resp.read().decode())
            for item in tree_data.get("tree", []):
                p = item["path"]
                if p.endswith(".qmd") and not Path(p).name.startswith((".", "_")):
                    qmd_files.append(p)
    except Exception as e:
        print(f"❌ Error al consultar la API de GitHub: {e}")
        return

    print(f"📄 Descargando {len(qmd_files)} capítulos en Markdown limpio...")
    index_lines = [
        f"# Índice General: {book_name}",
        f"**Autores:** {author}  ",
        "**Formato:** Quarto Book / Markdown (MIT Press 2024)\n",
        "> [!tip] Capítulos de Visión Moderna y Deep Learning",
        "> Contenido oficial extraído en formato Markdown nativo con ecuaciones KaTeX.\n",
        "## Capítulos y Secciones\n"
    ]

    for idx, qmd_name in enumerate(sorted(qmd_files), 1):
        raw_url = f"https://raw.githubusercontent.com/{repo_name}/main/{qmd_name}"
        stem = Path(qmd_name).stem
        out_file = out_dir / f"{slugify(stem)}.md"

        if out_file.exists() and not force:
            print(f"   [{idx}/{len(qmd_files)}] ⏩ {stem}.md (ya en local)")
            continue

        try:
            raw_req = urllib.request.Request(raw_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(raw_req, timeout=15) as raw_resp:
                content = raw_resp.read().decode("utf-8", errors="ignore")

            title = stem.replace("_", " ").title()
            title_match = re.search(r'^#\s+([^\{]+?)(?:\s*\{#.*?\})?$', content, re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip()

            # Clean Quarto cross-reference anchors like {#sec-...}
            content = re.sub(r'\{#sec-[^\}]+\}', '', content)
            # Normalize image links
            content = re.sub(r'!\[(.*?)\]\([^)]*(?:figures|images)/([^)]+)\)', r'![\1](images/\2)', content)

            frontmatter = [
                "---",
                f'book: "{book_name}"',
                f'author: "{author}"',
                f'chapter_title: "{title}"',
                "type: section_content",
                "---\n",
                f"# {title}\n",
                f"> **Libro:** {book_name}  ",
                f"> **Autores:** {author}  ",
                "> **Navegación:** [Índice General](./_INDEX.md)\n",
                "---\n"
            ]
            out_file.write_text("\n".join(frontmatter) + content, encoding="utf-8")
            index_lines.append(f"- [{title}]({out_file.name})")
            print(f"   [{idx}/{len(qmd_files)}] ✓ {title}", end="\r")
        except Exception as e:
            print(f"\n   ❌ Error en {qmd_name}: {e}")

    (out_dir / "_INDEX.md").write_text("\n".join(index_lines), encoding="utf-8")
    print(f"\n✓ Completado con éxito: {len(qmd_files)} capítulos guardados en {out_dir}")


def main():
    parser = argparse.ArgumentParser(description="Procesa y estructura libros en Markdown.")
    parser.add_argument("--book", type=str, default="all", help="ID del libro a procesar")
    parser.add_argument("--chapter", type=int, default=None, help="Capítulo específico")
    parser.add_argument("--force", action="store_true", help="Sobrescribir archivos existentes")
    parser.add_argument("--no-images", action="store_true", help="Omitir imágenes")
    args = parser.parse_args()

    if not CONFIG_PATH.exists():
        print(f"Error: {CONFIG_PATH} no encontrado.")
        sys.exit(1)

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    books = config.get("books", [])
    selected = [b for b in books if args.book == "all" or b["id"] == args.book]

    for b in selected:
        if b.get("type") == "pdf":
            process_pdf_book(b, target_chapter=args.chapter, force=args.force, extract_images=not args.no_images)
        elif b.get("type") == "github_quarto":
            process_quarto_repo(b, force=args.force)


if __name__ == "__main__":
    main()
