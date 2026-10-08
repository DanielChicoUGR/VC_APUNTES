#!/usr/bin/env python3
"""Locate textbook passages using vectors, BM25, or both; then read the sources."""
import argparse
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
DB_DIR = SKILL_DIR / "data" / "lancedb"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
BOOK_PATHS = {"szeliski": "Szeliski", "forsyth": "Forsyth_Ponce"}


def open_table():
    import lancedb
    if not DB_DIR.exists():
        raise FileNotFoundError("Database not found. Run build_index.py first.")
    return lancedb.connect(str(DB_DIR)).open_table("textbook_chunks")


def filtered(search, book_filter):
    if book_filter != "all":
        search = search.where(f"file_path LIKE 'docs_clase/textBook/{BOOK_PATHS[book_filter]}/%'")
    return search


def search_vector_db(query_text, top_k=4, book_filter="all", table=None):
    from fastembed import TextEmbedding
    if table is None:
        table = open_table()
    vector = next(TextEmbedding(MODEL_NAME).embed([query_text]))
    return filtered(table.search(vector).metric("cosine"), book_filter).limit(top_k).to_list()


def search_bm25(query_text, top_k=4, book_filter="all", table=None):
    if table is None:
        table = open_table()
    return filtered(table.search(query_text, query_type="fts", fts_columns="text"), book_filter).limit(top_k).to_list()


def clean_results(results):
    return [{**{k: v for k, v in row.items() if k != "vector"}, "rank": rank}
            for rank, row in enumerate(results, 1)]


def search(query_text, mode="vector", lexical_query=None, top_k=4, book_filter="all"):
    table = open_table()
    payload = {"query": query_text, "mode": mode, "lexical_query": lexical_query or query_text,
               "embeddings": [], "bm25": []}
    if mode in ("bm25", "both"):
        payload["bm25"] = clean_results(search_bm25(payload["lexical_query"], top_k, book_filter, table))
    if mode in ("vector", "both"):
        payload["embeddings"] = clean_results(search_vector_db(query_text, top_k, book_filter, table))
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Semantic query or lexical terms")
    parser.add_argument("--mode", choices=["vector", "bm25", "both"], default="vector")
    parser.add_argument("--lexical-query", help="Optional English terms for BM25; no automatic translation")
    parser.add_argument("--top-k", type=int, default=4, help="Maximum passages per engine")
    parser.add_argument("--book", choices=["szeliski", "forsyth", "all"], default="all")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.top_k < 1:
        parser.error("--top-k must be positive")
    try:
        payload = search(args.query, args.mode, args.lexical_query, args.top_k, args.book)
    except Exception as exc:
        message = str(exc)
        if args.mode in ("bm25", "both"):
            message += "\nIf the FTS index is missing, run build_index.py --fts-only."
        if args.json:
            print(json.dumps({"error": message}, ensure_ascii=False))
        else:
            print(message, file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Consulta: {args.query} | Modo: {args.mode}")
        for engine in ("embeddings", "bm25"):
            if (engine == "embeddings" and args.mode == "bm25") or (engine == "bm25" and args.mode == "vector"):
                continue
            print(f"\n{engine}: {len(payload[engine])} resultados")
            for row in payload[engine]:
                print(f"[{row['rank']}] {row['file_path']}\n  {row['section']} > {row['heading']}")
                metric = "_distance" if engine == "embeddings" else "_score"
                print(f"  {metric}: {row.get(metric)} | Páginas PDF: {row['pages_pdf']}")
                print(row['text'][:1200])
    return 0


if __name__ == "__main__":
    sys.exit(main())
