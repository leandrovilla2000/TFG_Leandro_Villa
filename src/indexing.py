from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.storage import InMemoryByteStore
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
import uuid
from filters import llm

def split_summarize_and_embed(docs):
    
    #Split documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    summarization_prompt = ChatPromptTemplate.from_template("Resume brevemente el siguiente documento:\n\n{doc}")
    summarization_chain = ({"doc": lambda x: x.page_content} | summarization_prompt | llm | StrOutputParser())
    summaries = summarization_chain.batch(splits, {"max_concurrency": 5})

    # Vectorstore for summaries
    vectorstore = Chroma(collection_name="summaries",
                         embedding_function=FastEmbedEmbeddings())
    
    # Full splits storage
    docstore = InMemoryByteStore()
    id_key = "doc_id"
    
    # Creates Retriever with both stores
    retriever = MultiVectorRetriever(vectorstore=vectorstore, byte_store=docstore, id_key=id_key)
    doc_ids = [str(uuid.uuid4()) for _ in splits]
    
    # Link full splits to summaries
    summary_docs = [Document(page_content=s, metadata={id_key: doc_ids[i]}) for i, s in enumerate(summaries)]
    
    # Add summary docs to vectorstore
    retriever.vectorstore.add_documents(summary_docs)
    # Add full splits to docstore
    retriever.docstore.mset(list(zip(doc_ids, splits)))

    return retriever