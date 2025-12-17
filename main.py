from fastapi import FastAPI, Query
import requests
import feedparser
from typing import Optional

app = FastAPI()

@app.get("/search-and-draft")
def search_and_draft(
    query: str = Query(..., description="Tema o palabras clave"),
    language: Optional[str] = Query("es", description="Idioma (es o en)"),
    maxResults: Optional[int] = Query(3, description="Número máximo de artículos")
):
    base_url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": maxResults,
        "sortBy": "relevance",
        "sortOrder": "descending"
    }

    response = requests.get(base_url, params=params)
    feed = feedparser.parse(response.text)

    articles = []
    for entry in feed.entries:
        articles.append({
            "title": entry.title,
            "summary": entry.summary,
            "authors": [author.name for author in entry.authors],
            "published": entry.published,
            "source": "arXiv",
            "link": entry.link
        })

    if not articles:
        return {"error": "No se encontraron artículos."}

    # Redacción automática basada en artículos obtenidos
    draft = f"### Redacción científica sobre: {query}

"
    draft += f"**Resumen**

"
    draft += f"Este artículo presenta una revisión de literatura sobre *{query}* utilizando fuentes open access indexadas como arXiv.

"

    draft += f"**Introducción**

"
    draft += f"La creciente relevancia del tema '{query}' ha motivado investigaciones recientes. A continuación, se resumen los hallazgos más relevantes.

"

    draft += f"**Metodología**

"
    draft += f"Se utilizó la API de arXiv para identificar publicaciones científicas recientes relacionadas con el tema '{query}'. Se seleccionaron los {len(articles)} artículos más relevantes.

"

    draft += f"**Resultados**

"
    for article in articles:
        draft += f"- {article['title']} ({article['published'][:10]}) por {', '.join(article['authors'])}.
  {article['summary'][:300]}...
  Fuente: {article['link']}

"

    draft += f"**Discusión**

"
    draft += f"Los estudios encontrados destacan distintas perspectivas sobre '{query}'. Se observa una tendencia a enfocarse en aplicaciones prácticas y desarrollo de nuevas metodologías.

"

    draft += f"**Conclusiones**

"
    draft += f"Existe un creciente cuerpo de literatura científica open access que apoya la importancia del estudio de '{query}'. Futuras investigaciones deben considerar enfoques interdisciplinarios y colaborativos.

"

    return {
        "query": query,
        "language": language,
        "results": articles,
        "draft": draft
    }
