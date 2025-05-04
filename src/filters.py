from pydantic import BaseModel, Field
from typing import Optional
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3")

class ForensicFileSearch(BaseModel):
    """Estructura para buscar documentos basados en metadatos."""
    content_search: Optional[str] = Field("", description="Términos clave")
    extension: Optional[str] = None
    filename_contains: Optional[str] = None
    min_size_kb: Optional[float] = None
    max_size_kb: Optional[float] = None
    earliest_date: Optional[str] = None
    latest_date: Optional[str] = None

templateMetadataFilter = """Eres un experto en convertir preguntas del usuario en filtros para una base de datos de documentos.
Únicamente completa los campos si el usuario es claro al mencionar algun metadato.
Debes devolver exclusivamente un objeto JSON que siga esta estructura. No devuelvas nada que no sea el objeto JSON. No comentes ni expliques nada.

Ejemplo de formato:

{{
  "content_search": "contenido a buscar",
  "extension": ".pdf",
  "filename_contains": "nombreArchivo",
  "min_size_kb": 0.0,
  "max_size_kb": 100.0,
  "earliest_date": "2023-01-01T00:00:00",
  "latest_date": "2024-01-01T00:00:00"
}}

Genera el objeto solicitado respecto a la siguiente pregunta: {question}"""

promptMetadataFilter = ChatPromptTemplate.from_template(templateMetadataFilter)
parser = JsonOutputParser(pydantic_schema=ForensicFileSearch)
query_analyzer = promptMetadataFilter | llm | parser

def generate_queries():
    templateMultiQuery = """Eres un asistente que genera múltiples consultas de búsqueda con el mismo significado de una sola consulta de entrada. \n
    Solo devuelve las consultas, una por línea, sin numerarlas ni comentar nada. Genera múltiples consultas de búsqueda relacionadas con: {question} \n
    Salida (4 consultas):"""
    promptMultiQuery = ChatPromptTemplate.from_template(templateMultiQuery)

    return promptMultiQuery | llm | (lambda x: x.split("\n"))

def metadata_filter_with_LLM(question, docs):
    query = query_analyzer.invoke({"question": question})
    if isinstance(query, dict):
        query = ForensicFileSearch(**query)

    filteredDocs = []
    for doc in docs:
        docMetadata = doc.metadata
        if query.extension and docMetadata.get("extension") != query.extension:
            continue
        if query.filename_contains and query.filename_contains not in docMetadata.get("filename", ""):
            continue
        filteredDocs.append(doc)

    print(filteredDocs)
    return query.content_search, filteredDocs