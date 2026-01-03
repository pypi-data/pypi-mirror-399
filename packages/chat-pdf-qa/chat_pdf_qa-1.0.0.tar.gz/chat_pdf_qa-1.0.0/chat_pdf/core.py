from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
import os

def load_pdf(pdf_path, api_key=None, chunk_size=1000, chunk_overlap=200, persist_directory=None, model_name="gpt-3.5-turbo", search_kwargs=None, system_prompt=None, llm=None):
    
    # Validate required parameters
    if not pdf_path:
        raise ValueError("pdf_path is required. Please provide the path to your PDF file.")
    
    if not api_key:
        raise ValueError("api_key is required. Please provide your OpenAI API key.")
    
    # Check if PDF file exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")
    
    # Check if the file is actually a PDF
    if not pdf_path.lower().endswith('.pdf'):
        raise ValueError("The provided file must be a PDF file.")
    
    loader = PyPDFLoader(pdf_path)

    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    split_docs = text_splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(api_key=api_key)

    db = Chroma.from_documents(split_docs,embeddings,persist_directory=persist_directory)

    return db

def ask_question(question, api_key=None, model_name="gpt-3.5-turbo", search_kwargs=None, system_prompt=None, llm=None, db=None):
    """
    Ask a question using the retrieval chain.
    
    Args:
        chain: The retrieval chain created by create_retrieval_chain_with_prompt
        question: The question to ask
    
    Returns:
        The answer as a string
    """
    # Validate required parameters
    if not question:
        raise ValueError("question is required. Please provide a question to ask.")
    
    if db is None:
        raise ValueError("db is required. Please provide a database object created from load_pdf().")
    
    if llm is None:
        if not api_key:
            raise ValueError("api_key is required when llm is not provided. Please provide your OpenAI API key.")
        llm = ChatOpenAI(model=model_name, temperature=0, api_key=api_key)
    
    # Set default search kwargs
    if search_kwargs is None:
        search_kwargs = {"k": 4}

    if system_prompt is None:
        system_prompt = (
            "You are a helpful assistant that answers questions based on the provided context. "
            "Use the following pieces of retrieved context to answer the question. "
            "If you don't know the answer based on the context, say that you don't know. "
            "Keep your answer concise and relevant.\n\n"
            "Context:\n{context}"
        )
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    # Create document chain (combines documents with prompt)
    document_chain = create_stuff_documents_chain(llm, prompt)
    
    # Create retriever from vector database
    retriever = db.as_retriever(search_kwargs=search_kwargs)
    
    # Create retrieval chain (retriever + document chain)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    
    response = retrieval_chain.invoke({"input": question})
    
    return response
    


def ask_question_with_sources(question, api_key=None, model_name="gpt-3.5-turbo", search_kwargs=None, system_prompt=None, llm=None, db=None):
    """
    Ask a question and get both the answer and source documents.
    
    Args:
        chain: The retrieval chain created by create_retrieval_chain_with_prompt
        question: The question to ask
    
    Returns:
        Dictionary with 'answer' and 'sources' (list of source documents)
    """
    # Validate required parameters
    if not question:
        raise ValueError("question is required. Please provide a question to ask.")
    
    if db is None:
        raise ValueError("db is required. Please provide a database object created from load_pdf().")
    
    if llm is None:
        if not api_key:
            raise ValueError("api_key is required when llm is not provided. Please provide your OpenAI API key.")
        llm = ChatOpenAI(model=model_name, temperature=0, api_key=api_key)
    
    # Set default search kwargs
    if search_kwargs is None:
        search_kwargs = {"k": 4}

    if system_prompt is None:
        system_prompt = (
            "You are a helpful assistant that answers questions based on the provided context. "
            "Use the following pieces of retrieved context to answer the question. "
            "If you don't know the answer based on the context, say that you don't know. "
            "Keep your answer concise and relevant.\n\n"
            "Context:\n{context}"
        )
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    # Create document chain (combines documents with prompt)
    document_chain = create_stuff_documents_chain(llm, prompt)
    
    # Create retriever from vector database
    retriever = db.as_retriever(search_kwargs=search_kwargs)
    
    # Create retrieval chain (retriever + document chain)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    
    response = retrieval_chain.invoke({"input": question})

    return {
        "answer": response["answer"],
        "sources": response["context"]
    }

