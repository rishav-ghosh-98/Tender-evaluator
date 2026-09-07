from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from pinecone import Pinecone

from .config import (
    EMBEDDING_MODEL_NAME,
    PINECONE_INDEX_NAME,
    get_pinecone_api_key,
)
from .models import TenderRequirements


REQUIREMENTS_PROMPT = ChatPromptTemplate.from_template("""
You are an AI assistant helping analyze a government tender document.

Extract the important procurement requirements from the tender context.

Return the information according to the TenderRequirements schema.

Rules:

1. Use ONLY information present in the tender.
2. Do not invent or assume information.
3. If information is unavailable, return "Not specified".
4. Preserve important numbers, dates and specifications.
5. Preserve technical specification identifiers exactly.
6. Preserve delivery conditions exactly.

Tender Context:

{context}
""")


def load_tender(tender_path: str, llm):
    documents = PyPDFLoader(tender_path).load()
    print("\n--- DOCUMENT ---")
    print(f"Number of pages: {len(documents)}")

    chunks = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    ).split_documents(documents)
    print("\n--- CHUNKING ---")
    print(f"Number of chunks: {len(chunks)}")

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    test_vector = embeddings.embed_query("What is the warranty period?")
    print("\n--- EMBEDDINGS ---")
    print(f"Embedding dimensions: {len(test_vector)}")

    index = Pinecone(api_key=get_pinecone_api_key()).Index(
        PINECONE_INDEX_NAME
    )
    vectorstore = PineconeVectorStore(
        index=index,
        embedding=embeddings
    )

    chunk_ids = [
        f"tender-21261162-chunk-{index}"
        for index in range(len(chunks))
    ]
    print("\n--- PINECONE BEFORE UPLOAD ---")
    print(index.describe_index_stats())
    vectorstore.add_documents(chunks, ids=chunk_ids)
    print("\n--- PINECONE AFTER UPLOAD ---")
    print(index.describe_index_stats())

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    tender_context = "\n\n".join(
        document.page_content
        for document in chunks
    )
    requirements = TenderRequirements.model_validate(
        llm.with_structured_output(TenderRequirements).invoke(
            REQUIREMENTS_PROMPT.invoke({"context": tender_context})
        )
    )

    print("\n--- STRUCTURED TENDER REQUIREMENTS ---")
    print(requirements)

    return requirements, retriever
