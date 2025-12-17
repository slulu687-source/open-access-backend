from fastapi import FastAPI, Query
import requests
import os
from typing import Optional

app = FastAPI(
    title="Scopus Scientific Search API",
    description="Búsqueda real de artículos indexados en Scopus (Elsevier)",
    version="1.0.0"
)

# 🔐 API Key desde variable de entorno
SCOPUS_API_KEY = os.getenv("SCOPUS_API_KEY")

SCOPUS_URL = "https://api.elsevier.com/content/search/scopus"

@app.get("/scopus-search")
def scopus_search(
    query: str = Query(..., description="Tema o palabras clave"),
    maxResults: Optional[int] = Query(10, description="Número de resultados")
):
    if not SCOPUS_API_KEY:
        return {"error": "API Key de Scopus no configurada"}

    headers = {
        "X-ELS-APIKey": SCOPUS_API_KEY,
        "Accept": "application/json"
    }

    params = {
        "query": query,
        "count": maxResults
    }

    response = requests.get(SCOPUS_URL, headers=headers, params=params)

    if response.status_code != 200:
        return {
            "error": "Error al consultar Scopus",
            "status_code": response.status_code,
            "details": response.text
        }

    data = response.json()
    entries = data.get("search-results", {}).get("entry", [])

    articles = []

    for entry in entries:
        articles.append({
            "title": entry.get("dc:title"),
            "authors": entry.get("dc:creator"),
            "year": entry.get("prism:coverDate", "")[:4],
            "journal": entry.get("prism:publicationName"),
            "doi": entry.get("prism:doi"),
            "scopus_id": entry.get("dc:identifier"),
            "link": entry.get("prism:url")
        })

    return {
        "query": query,
        "total_results": len(articles),
        "articles": articles
    }

