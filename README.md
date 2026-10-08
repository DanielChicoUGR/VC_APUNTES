# 👁️ Visión por Computador — Vault Colaborativo de Apuntes

[![Obsidian](https://img.shields.io/badge/Obsidian-Vault-7C3AED?logo=obsidian&logoColor=white)](https://obsidian.md/)
[![LanceDB](https://img.shields.io/badge/Vector_DB-LanceDB-00D2B4)](https://lancedb.com/)
[![FastEmbed](https://img.shields.io/badge/Embeddings-FastEmbed_ONNX-blue)](https://qdrant.github.io/fastembed/)
[![Python](https://img.shields.io/badge/Python-3.10%2B_%7C_uv-FFD43B?logo=python&logoColor=blue)](https://github.com/astral-sh/uv)

Repositorio central y colaborativo para estudiantes de **Visión por Computador**. Combina los apuntes teóricos de la asignatura con un **pipeline de ingesta y búsqueda vectorial semántica (RAG)** sobre los libros de texto canónicos de la disciplina.

---

## ⚡ Inicio Rápido (3 Pasos)

### 1. Clonar el repositorio
```bash
git clone https://github.com/DanielChicoUGR/VC_APUNTES.git
cd VC_APUNTES
```

### 2. Inicializar el entorno en 1 solo comando
Ejecuta el script de preparación. Este script instalará automáticamente `uv` (si no lo tienes), descargará los libros de texto canónicos, los procesará a Markdown con fórmulas e imágenes, y creará la base de datos vectorial local:

```bash
./setup.sh
```

### 3. Abrir en Obsidian
Abre la aplicación [Obsidian](https://obsidian.md/) y selecciona **"Open folder as vault"**, apuntando a la carpeta clonada `VC_APUNTES`.
* Los plugins (Mermaid Tools, Admonitions, Catppuccin Theme) ya vienen preconfigurados.

---

## 📚 Colección Bibliográfica Canónica Integrada

El repositorio procesa y permite realizar búsquedas semánticas sobre los siguientes textos de referencia:

| Disciplina | Libro / Documento | Autores | Año / Edición | Formato |
| :--- | :--- | :--- | :---: | :---: |
| **Visión Clásica** | *Computer Vision: Algorithms and Applications* | Richard Szeliski | 2nd Ed. (2022) | PDF $\to$ MD |
| **Visión Clásica** | *Computer Vision: A Modern Approach* | D. Forsyth & J. Ponce | 2nd Ed. (2012) | PDF $\to$ MD |
| **Geometría y 3D** | *Multiple View Geometry in Computer Vision* | R. Hartley & A. Zisserman | 2nd Ed. (2011) | PDF $\to$ MD |
| **Deep Learning** | *Understanding Deep Learning* | Simon J.D. Prince | MIT Press (2023) | PDF $\to$ MD |
| **Visión Moderna** | *Foundations of Computer Vision* | A. Torralba, P. Isola, W.T. Freeman | MIT Press (2024) | Quarto $\to$ MD |
| **Fundamentos** | *Matrix Calculus (for Machine Learning and Beyond)* | P. Bright, A. Edelman, S.G. Johnson | arXiv (2025) | PDF $\to$ MD |

---

## 🔍 Búsqueda Local (Vectores y BM25)

El repositorio incluye un motor de búsqueda vectorial local basado en **LanceDB** y **FastEmbed** (`paraphrase-multilingual-MiniLM-L12-v2`). Permite hacer preguntas en **español** para encontrar párrafos, fórmulas y algoritmos en los libros en **inglés**:

### Consultar desde la terminal:
```bash
# Búsqueda general:
uv run --with lancedb,fastembed python3 .agents/skills/vc-textbook-rag/scripts/query.py "cómo funciona el filtro bilateral para reducir ruido"

# Filtrar por libro específico:
uv run --with lancedb,fastembed python3 .agents/skills/vc-textbook-rag/scripts/query.py "matriz fundamental y geometria epipolar" --book szeliski

# Salida en formato JSON (para agentes de IA):
uv run --with lancedb,fastembed python3 .agents/skills/vc-textbook-rag/scripts/query.py "harris corner detector eigenvalues" --top-k 2 --json

# Preparar BM25 sobre el índice existente, sin recalcular vectores:
uv run --with lancedb,pyyaml python3 .agents/skills/vc-textbook-rag/scripts/build_index.py --fts-only

# Solo BM25, sin cargar FastEmbed:
uv run --with lancedb python3 .agents/skills/vc-textbook-rag/scripts/query.py "Harris corner detector" --mode bm25 --json

# Ambos motores con consultas separadas:
uv run --with lancedb,fastembed python3 .agents/skills/vc-textbook-rag/scripts/query.py "detector de esquinas Harris" --mode both --lexical-query "Harris corner detector" --json
```

---

## 📂 Estructura del Repositorio

```text
VC_APUNTES/
├── Tema 1/ ... Tema 5/           # Apuntes colaborativos de la asignatura
├── docs_clase/
│   ├── T1/, T2/                  # Diapositivas y material de clase
│   └── textBook/                 # Libros procesados en Markdown modular con sus imágenes
├── .agents/skills/
│   └── vc-textbook-rag/          # Skill de IA: indexador, buscador y base de datos LanceDB
├── scripts/
│   ├── books_config.json         # Catálogo de libros y URLs de descarga
│   ├── process_textbooks.py      # Pipeline de conversión PDF/Quarto a Markdown
│   └── setup_repo.py             # Orquestador del setup automático
├── setup.sh                      # Instalador en 1 solo paso
└── CONTRIBUTING.md               # Guía de estilo y colaboración para alumnos
```

---

## 🤝 Cómo Colaborar

Cualquier alumno puede proponer mejoras, corregir fórmulas, añadir exámenes resueltos o ampliar temas. Consulta las normas en [CONTRIBUTING.md](CONTRIBUTING.md).


### Referencias del buscador

- **VC_APUNTES**. *Recuperación y lectura de fuentes*: [skill](.agents/skills/vc-textbook-rag/SKILL.md), [query.py](.agents/skills/vc-textbook-rag/scripts/query.py). El JSON devuelve listas `embeddings` y `bm25`, sustituyendo `results`; tras localizar archivos, hay que leerlos y seguir enlaces pertinentes antes de responder con referencias.
- **LanceDB contributors**. *LanceDB Python API*, índices FTS y búsqueda BM25: [documentación oficial](https://lancedb.github.io/lancedb/python/python/).
