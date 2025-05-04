from filters import generate_queries, metadata_filter_with_LLM
from indexing import split_summarize_and_embed
from generation import retrieval_and_generation
from langchain.load import dumps, loads

def reciprocal_rank_fusion(results):
    scores = {}
    k = 60
    for docs in results:
        for rank, doc in enumerate(docs):
            key = dumps(doc)
            scores[key] = scores.get(key, 0) + 1 / (rank + k)
    return [loads(doc) for doc, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)]

def final_pipeline_rag(question, docs):
    multiqueries = generate_queries().invoke({"question": question})
    print(multiqueries)
    all_filtered = []
    for query in multiqueries:
        _, filtered = metadata_filter_with_LLM(query, docs)
        if filtered:
            all_filtered.extend(filtered)
    if not all_filtered:
        return "No se encontraron documentos."

    reranked = reciprocal_rank_fusion([all_filtered])
    print(reranked)
    retriever = split_summarize_and_embed(reranked)
    context_docs = retriever.invoke(question)
    return retrieval_and_generation(context_docs, question)