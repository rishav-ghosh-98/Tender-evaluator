from langchain_core.prompts import ChatPromptTemplate


RAG_PROMPT = ChatPromptTemplate.from_template("""
You are an assistant helping a government procurement official
understand a tender document.

Answer the question using ONLY the provided tender context.

Do not use outside knowledge.

If the answer cannot be found in the context, say:

"I could not find this information in the tender document."

Tender Context:
{context}

Question:
{question}
""")


def answer_question(query: str, retriever, llm):
    documents = retriever.invoke(query)

    print("\n--- RETRIEVAL RESULTS ---")
    for index, document in enumerate(documents, start=1):
        print(f"\nResult {index}")
        print(f"Page: {document.metadata.get('page_label')}")
        print(document.page_content)

    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    response = llm.invoke(RAG_PROMPT.invoke({
        "context": context,
        "question": query
    }))

    print("\n--- RAG RESPONSE ---")
    print(response.content)

    print("\n--- RAG SOURCES ---")
    for index, document in enumerate(documents, start=1):
        print(f"\nSource {index}")
        print(f"Page: {document.metadata.get('page_label')}")
        print(f"Content: {document.page_content}")

    return response, documents
