from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from filters import llm

def retrieval_and_generation(docs, question):
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    templateRAG = """Responde la siguiente pregunta en base a este contexto:
    {context}
    Pregunta: {question}
    """
    promptRAG = ChatPromptTemplate.from_template(templateRAG)
    chainRAG = promptRAG | llm | StrOutputParser()
    return chainRAG.invoke({"context": format_docs(docs), "question": question})
