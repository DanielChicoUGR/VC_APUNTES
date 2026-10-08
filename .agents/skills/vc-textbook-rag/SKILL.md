---
name: vc-textbook-rag
description: Locate Computer Vision textbook and class-document sources using multilingual vector search, BM25, or both, then read original files and relevant internal links before explaining algorithms, mathematics, or drafting notes. Personal Tema notes are not indexed.
---

# Computer Vision source retrieval

## Required workflow

Question → locate relevant files (vector / BM25 / both) → read original files → respond with references.

Use the MCP tool `search_textbooks` (preferred) or `scripts/query.py` via CLI to locate evidence in `docs_clase/`. Results are pointers and excerpts, not a substitute for reading the sources. Personal `Tema 1`–`Tema 5` notes are not indexed.

1. Extract the technical concepts. Use `vector` for descriptive or multilingual questions, `bm25` for named concepts and exact terms, and `both` when both signals are useful. The default remains `vector`.
2. For BM25 over English books, supply English technical terms, preserving proper names and acronyms. Use `--lexical-query` (or parameter `lexical_query`) to retain the original semantic question. For Spanish class material retain Spanish terms; if necessary query both languages. The script does not translate.
3. Inspect both result lists when requested. Deduplicate source reads by `file_path`, keeping all relevant `heading` values. Read the returned source files with an available file-reading tool. For long files, locate and read the relevant sections and enough surrounding context to establish definitions, assumptions and equations.
4. Follow Markdown links and Obsidian wikilinks when they provide needed definitions, derivations or related evidence. Resolve relative Markdown paths against the source directory and heading anchors inside the target file; resolve vault wikilinks within the vault. Inspect equation/figure images when needed. Track already-read files and sections to avoid loops and redundant reads. Do not traverse navigation links indiscriminately.
5. If evidence is insufficient, reformulate or widen retrieval. Never claim a source was read based only on its search excerpt. Cite only consulted sources, with exact chapter/section and PDF pages when available, using the channel-specific format in AGENTS.md.

If the exact source path is already known, read it directly rather than repeating retrieval.

## Commands

From the repository root:

```bash
# MCP Server (Model Context Protocol stdio)
uv run --with mcp,lancedb,fastembed python3 .agents/skills/vc-textbook-rag/scripts/server.py

# Multilingual semantic search
uv run --with lancedb,fastembed python3 .agents/skills/vc-textbook-rag/scripts/query.py "filtro bilateral" --mode vector --top-k 4 --json

# Lexical search: no FastEmbed import or model loading
uv run --with lancedb python3 .agents/skills/vc-textbook-rag/scripts/query.py "bilateral filter" --mode bm25 --book szeliski --json

# Independent lists from both engines (no ranking fusion)
uv run --with lancedb,fastembed python3 .agents/skills/vc-textbook-rag/scripts/query.py "¿Cómo funciona el filtro bilateral?" --mode both --lexical-query "bilateral filter" --json

# Prepare BM25 on existing indexed text without recalculating vectors
uv run --with lancedb,pyyaml python3 .agents/skills/vc-textbook-rag/scripts/build_index.py --fts-only

# Rebuild both indexes after changing corpus content
uv run --with lancedb,fastembed,pyyaml python3 .agents/skills/vc-textbook-rag/scripts/build_index.py --force
```

Database: `data/lancedb/`, table `textbook_chunks`. Vector model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. BM25 uses a persistent LanceDB full-text index over `text`. Supported book filters: `szeliski`, `forsyth`, `all`.

`--fts-only` indexes the stored text, not changed source files. Changes to source content require a full rebuild. Run preparation once before using BM25; queries do not create indexes. Current LanceDB native FTS is required; verified with LanceDB 0.40.0.

## JSON contract

```json
{
  "query": "filtro bilateral",
  "mode": "both",
  "lexical_query": "bilateral filter",
  "embeddings": [],
  "bm25": []
}
```

Each populated list contains the existing passage fields (`id`, `book`, `chapter`, `section`, `heading`, `pages_pdf`, `file_path`, `text`) and a 1-based `rank`. Vector results have `_distance` (lower is closer); BM25 has `_score` (higher is more relevant). Scores are not probabilities and cannot be compared across engines. Vectors are omitted. Unrequested lists remain empty. `--top-k` limits passages per engine, not unique files. The same file or passage can occur in both lists; preserve that agreement while reading the file only as needed.

This replaces the previous JSON `results` key; update callers to read `embeddings` and `bm25`. No `results` compatibility alias is emitted.

## References

- LanceDB contributors. *LanceDB Python API*, `create_fts_index` and full-text query builders: [official API](https://lancedb.github.io/lancedb/python/python/).
- VC_APUNTES. *Source retrieval implementation*: [query.py](scripts/query.py), [server.py](scripts/server.py), [build_index.py](scripts/build_index.py).
