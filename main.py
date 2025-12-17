from fastapi import FastAPI, Query
import requests
import feedparser

app = FastAPI()

@app.get("/open-access-search")
def open_access_search(query: str, maxResults: int = 5, language: str = "es"):
    results = []

    # === arXiv ===
    arxiv_url = "http://export.arxiv.org/api/query"
    arxiv_params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": maxResults
    }
    arxiv_response = requests.get(arxiv_url, params=arxiv_params)
    arxiv_feed = feedparser.parse(arxiv_response.text)
    for entry in arxiv_feed.entries:
        results.append({
            "title": entry.title,
            "summary": entry.summary,
            "authors": [author.name for author in entry.authors],
            "published": entry.published,
            "source": "arXiv",
            "link": entry.link
        })

    # === PubMed Central ===
    esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    pm_params = {
        "db": "pmc",
        "term": query,
        "retmax": maxResults,
        "retmode": "json"
    }
    search_response = requests.get(esearch_url, params=pm_params)
    ids_text = search_response.text
    if "<IdList>" in ids_text:
        pmids = [line.strip() for line in ids_text.split("<Id>")[1:] if "</Id>" in line]
        for pmid in pmids:
            pmid_clean = pmid.split("</Id>")[0]
            results.append({
                "title": f"Artículo PMC ID: {pmid_clean}",
                "summary": "Requiere extracción XML para ver contenido.",
                "authors": [],
                "published": "Desconocido",
                "source": "PubMed Central",
                "link": f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmid_clean}/"
            })

    return {
        "query": query,
        "language": language,
        "results": results[:maxResults * 2]  # combinar resultados de ambas fuentes
    }
