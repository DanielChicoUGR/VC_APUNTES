#!/usr/bin/env python3
"""MCP Server for Computer Vision Textbook RAG."""
import sys
from pathlib import Path
from typing import Literal

# Ensure scripts directory is on sys.path to import query module
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

try:
    from mcp.server.mcpserver import MCPServer
    mcp = MCPServer("vc-textbook-rag")
except (ImportError, ModuleNotFoundError):
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("vc-textbook-rag")

from query import search


@mcp.tool()
def search_textbooks(
    query: str,
    mode: Literal["vector", "bm25", "both"] = "vector",
    lexical_query: str | None = None,
    top_k: int = 4,
    book: Literal["szeliski", "forsyth", "all"] = "all",
) -> dict:
    """Busca conceptos, fórmulas y algoritmos en los libros canónicos de Visión por Computador.

    Devuelve fragmentos con file_path, sección, páginas PDF y ranking de relevancia.
    Deduplica lecturas entre embeddings y bm25 y lee los archivos originales antes de responder.

    Args:
        query: Pregunta técnica o conceptos clave (en español o inglés).
        mode: 'vector' (semántico denso), 'bm25' (léxico exacto) o 'both' (ambos motores en paralelo).
        lexical_query: Términos opcionales en inglés para BM25 si la consulta semántica principal es en español.
        top_k: Máximo de pasajes devueltos por cada motor (default: 4).
        book: Filtro por libro: 'szeliski', 'forsyth' o 'all'.
    """
    return search(
        query_text=query,
        mode=mode,
        lexical_query=lexical_query,
        top_k=top_k,
        book_filter=book,
    )


if __name__ == "__main__":
    mcp.run()
