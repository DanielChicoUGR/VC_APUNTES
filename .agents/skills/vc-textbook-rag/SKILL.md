---
name: vc-textbook-rag
description: Search and retrieve relevant sections, formulas, diagrams, and explanations from Computer Vision textbooks (Richard Szeliski and Forsyth & Ponce) using local semantic vector search (LanceDB + FastEmbed). Use whenever answering theoretical questions, explaining algorithms (SIFT, Harris, bilateral filter, epipolar geometry, optical flow, CNNs), deriving mathematical formulas, or contrasting lecture notes with textbook definitions.
---

# Computer Vision Textbook RAG (LanceDB + FastEmbed)

This skill provides semantic vector search over the modularized Computer Vision textbooks:
- **Richard Szeliski**, *Computer Vision: Algorithms and Applications* (2nd Edition)
- **David Forsyth & Jean Ponce**, *Computer Vision: A Modern Approach*
- Complementary class documents in `docs_clase/`

It uses a local, serverless vector database (**LanceDB**) and a CPU-optimized multilingual embedding model (**FastEmbed** / `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`).

---

## When to Use This Skill

Activate and use this skill whenever:
1. **Theoretical or algorithmic questions:** The user asks how an algorithm works (e.g., Canny, Harris, SIFT, HOG, RANSAC, Kalman Filter, Epipolar Geometry, Bundle Adjustment, Bilateral Filter).
2. **Mathematical definitions & derivations:** The user or agent needs exact formulas, matrix representations, or formal proofs with proper KaTeX/LaTeX formatting.
3. **Multilingual lookups:** The user asks a question in Spanish (e.g., *"¿cómo funciona el flujo óptico de Lucas-Kanade?"*), and the agent needs to find the exact English textbook section (*"Lucas-Kanade optical flow"*).
4. **Drafting or expanding course notes:** When generating notes for `Tema 1` to `Tema 5` and needing rigorous textbook depth.

## When NOT to Use This Skill
- Do **not** use this to query personal notes in `Tema 1` to `Tema 5` (those are the student's personal notes and are not in the index).
- Do **not** use this for simple file-tree queries or when the exact path is already known (use direct file viewing instead).

---

## How to Query the Vector Database

The search script is located at:
`.agents/skills/vc-textbook-rag/scripts/query.py`

### 1. Basic Semantic Search (Human / Terminal Output)
```bash
uv run --with lancedb,fastembed python3 .agents/skills/vc-textbook-rag/scripts/query.py "<consulta en español o inglés>"
```

### 2. Filtering by Textbook
```bash
# Query only Szeliski:
uv run --with lancedb,fastembed python3 .agents/skills/vc-textbook-rag/scripts/query.py "filtro bilateral" --book szeliski

# Query only Forsyth & Ponce:
uv run --with lancedb,fastembed python3 .agents/skills/vc-textbook-rag/scripts/query.py "linear filters convolution" --book forsyth
```

### 3. Programmatic JSON Output (For LLM Agents)
To receive machine-readable JSON containing the top chunks, file paths, and exact text excerpts:
```bash
uv run --with lancedb,fastembed python3 .agents/skills/vc-textbook-rag/scripts/query.py "epipolar geometry fundamental matrix" --top-k 3 --json
```

---

## How to Rebuild or Update the Vector Index

If new textbooks or class documents are added to `docs_clase/`, the index can be recreated with:

```bash
uv run --with lancedb,fastembed,pyyaml python3 .agents/skills/vc-textbook-rag/scripts/build_index.py --force
```

- **Database location:** `.agents/skills/vc-textbook-rag/data/lancedb/`
- **Table name:** `textbook_chunks`

---

## Recommended Agent Workflow

When generating or refining notes for the user:
1. **Query:** Run `query.py` with `--top-k 3` or `--json` using key technical terms.
2. **Inspect:** If a result provides a highly relevant file path (e.g. `docs_clase/textBook/Szeliski/Chapter_07_Feature_detection_and_matching/07.1_Points_and_patches.md`), read that specific file using `view_file`.
3. **Synthesize:** Explain the concept in the student's notes with intuitive explanations, LaTeX mathematical formulas, and algorithm steps.
