#!/usr/bin/env python3
"""
query.py
========
Performs semantic vector searches against the local LanceDB index of Computer Vision textbooks.
Supports multilingual queries (Spanish queries find English text) using FastEmbed.

Usage:
    uv run --with lancedb,fastembed python3 .agents/skills/vc-textbook-rag/scripts/query.py "<consulta>" [OPTIONS]

Options:
    --top-k N             Number of top results to return (default: 4)
    --book [szeliski|forsyth|all] Filter by book (default: all)
    --json                Output results in JSON format (for agent programmatic use)
"""

import sys
import json
import argparse
from pathlib import Path

try:
    import lancedb
    from fastembed import TextEmbedding
except ImportError:
    print("Error: Missing required packages. Run with:")
    print("uv run --with lancedb,fastembed python3 .agents/skills/vc-textbook-rag/scripts/query.py \"<query>\"")
    sys.exit(1)

SKILL_DIR = Path(__file__).resolve().parents[1]
DB_DIR = SKILL_DIR / "data" / "lancedb"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def search_vector_db(query_text: str, top_k: int = 4, book_filter: str = "all") -> list:
    """Executes a semantic vector search on the LanceDB textbook index."""
    if not DB_DIR.exists():
        raise FileNotFoundError(f"Database not found at {DB_DIR}. Run build_index.py first.")

    db = lancedb.connect(str(DB_DIR))
    table_name = "textbook_chunks"
    try:
        table = db.open_table(table_name)
    except Exception:
        raise ValueError(f"Table '{table_name}' does not exist in {DB_DIR}. Run build_index.py first.")

    # Embed query
    model = TextEmbedding(MODEL_NAME)
    query_emb = list(model.embed([query_text]))[0]

    # Search
    search_query = table.search(query_emb).metric("cosine")
    
    if book_filter != "all":
        # Case-insensitive filtering
        filter_pattern = "Szeliski" if book_filter.lower() == "szeliski" else "Forsyth"
        search_query = search_query.where(f"book LIKE '%{filter_pattern}%'")

    results = search_query.limit(top_k).to_list()
    return results


def main():
    parser = argparse.ArgumentParser(description="Query the local textbook RAG vector database.")
    parser.add_argument("query", type=str, help="Search query (in Spanish or English)")
    parser.add_argument("--top-k", type=int, default=4, help="Number of results to return")
    parser.add_argument("--book", choices=["szeliski", "forsyth", "all"], default="all",
                        help="Filter by specific textbook")
    parser.add_argument("--json", action="store_true", help="Output raw JSON for LLM / script consumption")

    args = parser.parse_args()

    try:
        results = search_vector_db(args.query, top_k=args.top_k, book_filter=args.book)
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"❌ Error durante la búsqueda: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        # Clean vectors from output before serialization
        clean_results = []
        for r in results:
            item = dict(r)
            item.pop("vector", None)
            clean_results.append(item)
        print(json.dumps({"query": args.query, "results": clean_results}, indent=2, ensure_ascii=False))
        return

    # Formatted terminal output
    print("\n" + "=" * 75)
    print(f"🔍 Consulta Semántica: \"{args.query}\"")
    print(f"📚 Resultados encontrados: {len(results)} (Filtro libro: {args.book})")
    print("=" * 75)

    if not results:
        print("No se encontraron fragmentos relevantes para esta consulta.")
        return

    for idx, r in enumerate(results, 1):
        dist = r.get("_distance", 0.0)
        # Cosine distance to similarity percentage estimate
        similarity = max(0.0, 1.0 - dist) * 100

        print(f"\n[{idx}] 📖 {r['book']} | 📂 {r['chapter']}")
        print(f"    🏷️  Sección: {r['section']} > {r['heading']}")
        print(f"    📄 Páginas PDF: {r['pages_pdf']}  |  🔗 Archivo: {r['file_path']}")
        print(f"    🎯 Similitud: {similarity:.1f}% (Distancia coseno: {dist:.4f})")
        print("    " + "-" * 71)

        # Show snippet with indent
        text = r['text'].strip()
        lines = text.splitlines()
        preview = lines[:12]
        for l in preview:
            print(f"    {l}")
        if len(lines) > 12:
            print(f"    ... [+{len(lines) - 12} líneas adicionales en el archivo]")

    print("\n" + "=" * 75 + "\n")


if __name__ == "__main__":
    main()
