"""
Document Q&A with RAG (Retrieval-Augmented Generation)
Uses FAISS as vector store for document embeddings (if available, falls back to in-memory store)
Supports PDF and TXT files

Note: To use FAISS for better performance, install the faiss-cpu package:
      pip install faiss-cpu
      If FAISS is not available, the system will fall back to an in-memory vector store.
"""

import streamlit as st
import os
import tempfile
import shutil
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import io
import pickle

# LangChain imports - updated for latest versions
try:
    # Modern LangChain imports (0.3.x)
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    from langchain.prompts import PromptTemplate
    
    # Try importing FAISS, fall back to in-memory store if not available
    try:
        from langchain_community.vectorstores import FAISS
        FAISS_AVAILABLE = True
    except ImportError:
        from langchain_community.vectorstores.memory import MemoryVectorStore
        FAISS_AVAILABLE = False
        
    from langchain_community.document_loaders import PyPDFLoader, TextLoader
    from langchain_openai import OpenAI
    from langchain_openai import OpenAIEmbeddings
    from langchain.chains import RetrievalQA
    LANGCHAIN_AVAILABLE = True
except ImportError:
    try:
        # Fallback to older imports (0.0.x)
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.embeddings.openai import OpenAIEmbeddings
        
        # Try importing FAISS, fall back to in-memory store if not available
        try:
            from langchain.vectorstores import FAISS
            FAISS_AVAILABLE = True
        except ImportError:
            from langchain.vectorstores import InMemoryVectorStore as MemoryVectorStore
            FAISS_AVAILABLE = False
            
        from langchain.document_loaders import PyPDFLoader, TextLoader
        from langchain.schema import Document
        from langchain.chains import RetrievalQA
        from langchain.llms import OpenAI
        from langchain.prompts import PromptTemplate
        LANGCHAIN_AVAILABLE = True
    except ImportError:
        LANGCHAIN_AVAILABLE = False
        st.error("Some LangChain components not available. Please check your installation.")

# PDF processing
try:
    import PyPDF2
    import io
    PDF_AVAILABLE = True
except ImportError:
    try:
        import pypdf as PyPDF2
        import io
        PDF_AVAILABLE = True
    except ImportError:
        PDF_AVAILABLE = False
        st.warning("PyPDF2 not available. PDF processing will be limited.")

class DocumentQARAG:
    """Document Q&A with RAG using FAISS (with fallback to in-memory store) - simplified version with minimal logging"""
    
    def __init__(self, api_key: str):
        """Initialize the Document Q&A RAG system"""
        if not LANGCHAIN_AVAILABLE:
            raise ValueError("Required LangChain components not available. Please check your installation.")
        
        self.api_key = api_key
        self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        self.llm = OpenAI(temperature=0.7, openai_api_key=api_key)
        
        # No client initialization needed for FAISS or in-memory store
        self.vectorstore = None
        self.qa_chain = None
        
        # Generate a unique ID for this session
        self.session_id = f"qa_session_{uuid.uuid4().hex[:8]}"
        
        # Create index directory if using FAISS
        if FAISS_AVAILABLE:
            os.makedirs("./faiss_indexes", exist_ok=True)
        
        # Text splitter for documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from uploaded PDF file - with minimal logging"""
        if not PDF_AVAILABLE:
            return ""
        
        try:
            # Create a BytesIO object from the uploaded file's content
            bytes_data = pdf_file.getvalue()
            pdf_stream = io.BytesIO(bytes_data)
            
            # Reset stream position
            pdf_file.seek(0)
            
            # Create PdfReader object
            pdf_reader = PyPDF2.PdfReader(pdf_stream)
            
            text = ""
            
            # Extract text from each page
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
                    
            return text
            
        except Exception:
            # Silently fail and return empty string
            return ""
    
    def extract_text_from_txt(self, txt_file) -> str:
        """Extract text from uploaded TXT file - with minimal logging"""
        try:
            # Reset file pointer
            txt_file.seek(0)
            
            # Read text file content
            text = txt_file.read().decode('utf-8')
            return text
            
        except UnicodeDecodeError:
            # Try with different encodings if UTF-8 fails
            try:
                txt_file.seek(0)
                text = txt_file.read().decode('latin-1')
                return text
            except Exception:
                return ""
        except Exception:
            return ""
    
    def process_documents(self, uploaded_files: List) -> bool:
        """Process uploaded documents and create vector store - with minimal logging"""
        try:
            all_documents = []
            
            for uploaded_file in uploaded_files:
                # Get file extension
                file_extension = uploaded_file.name.split('.')[-1].lower()
                
                if file_extension == 'pdf':
                    text = self.extract_text_from_pdf(uploaded_file)
                elif file_extension == 'txt':
                    text = self.extract_text_from_txt(uploaded_file)
                else:
                    # Skip unsupported files silently
                    continue
                
                if text.strip():
                    # Split text into chunks
                    chunks = self.text_splitter.split_text(text)
                    
                    # Create Document objects
                    for i, chunk in enumerate(chunks):
                        doc = Document(
                            page_content=chunk,
                            metadata={
                                "source": uploaded_file.name,
                                "chunk_id": i,
                                "upload_time": datetime.now().isoformat()
                            }
                        )
                        all_documents.append(doc)
            
            if not all_documents:
                st.error("No valid text content found in uploaded files.")
                return False
            
            # Create vector store based on available backend
            if FAISS_AVAILABLE:
                # Create vector store with FAISS
                self.vectorstore = FAISS.from_documents(
                    documents=all_documents,
                    embedding=self.embeddings
                )
                
                # Save the FAISS index
                faiss_index_path = f"./faiss_indexes/{self.session_id}"
                self.vectorstore.save_local(faiss_index_path)
            else:
                # Fallback to in-memory vector store
                self.vectorstore = MemoryVectorStore.from_documents(
                    documents=all_documents,
                    embedding=self.embeddings
                )
            
            # Create QA chain
            self.create_qa_chain()
            
            return True
            
        except Exception as e:
            st.error(f"Error processing documents: {str(e)}")
            return False
    
    def create_qa_chain(self):
        """Create the Question-Answering chain - silently"""
        try:
            # Custom prompt template for better answers
            prompt_template = """
            You are a helpful AI assistant that answers questions based on the provided document context.
            Use the following pieces of context to answer the user's question. If you don't know the answer
            based on the context, just say that you don't know. Don't make up an answer.
            
            Context:
            {context}
            
            Question: {question}
            
            Helpful Answer:
            """
            
            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            # Create retrieval QA chain
            retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}  # Retrieve top 3 relevant chunks
            )
            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={"prompt": PROMPT},
                return_source_documents=True
            )
            
        except Exception as e:
            st.error(f"Error creating QA chain: {str(e)}")
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """Ask a question about the uploaded documents - with minimal logging"""
        try:
            if not self.qa_chain:
                return {
                    "answer": "Please upload and process documents first.",
                    "sources": [],
                    "error": "No documents processed"
                }
            
            if not question or not question.strip():
                return {
                    "answer": "Please enter a valid question.",
                    "sources": [],
                    "error": "Empty question"
                }
            
            # Get answer from QA chain
            result = self.qa_chain({"query": question})
            
            # Extract source information
            sources = []
            if "source_documents" in result:
                for doc in result["source_documents"]:
                    sources.append({
                        "source": doc.metadata.get("source", "Unknown"),
                        "chunk_id": doc.metadata.get("chunk_id", 0),
                        "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                    })
            
            return {
                "answer": result.get("result", "No answer found."),
                "sources": sources,
                "error": None
            }
            
        except Exception as e:
            return {
                "answer": f"Error answering question: {str(e)}. Please try a different question or reload the documents.",
                "sources": [],
                "error": str(e)
            }
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if FAISS_AVAILABLE:
                # Clean up FAISS index files
                faiss_index_path = f"./faiss_indexes/{self.session_id}"
                if os.path.exists(faiss_index_path):
                    try:
                        shutil.rmtree(faiss_index_path)
                    except:
                        pass  # Ignore errors in cleanup
            # For in-memory store, no cleanup is needed
        except Exception as e:
            print(f"Cleanup error: {e}")

def create_document_qa_interface():
    """Create the Document Q&A interface with simplified UX"""
    st.subheader("📄 Document Q&A")
    
    # Check dependencies silently
    if not LANGCHAIN_AVAILABLE:
        st.error("Required components not available. Please check your installation.")
        return
    
    # Initialize session state for document QA
    if 'doc_qa_system' not in st.session_state:
        st.session_state.doc_qa_system = None
    if 'doc_qa_files_processed' not in st.session_state:
        st.session_state.doc_qa_files_processed = False
    if 'doc_qa_chat_history' not in st.session_state:
        st.session_state.doc_qa_chat_history = []
    
    # Simplified UI with two columns
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Determine supported file types silently
        supported_types = ['txt']
        if PDF_AVAILABLE:
            supported_types.append('pdf')
        
        # File upload section - more compact
        uploaded_files = st.file_uploader(
            "Upload Documents",
            type=supported_types,
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        
        # Process button and clear button in same column
        if uploaded_files:
            process_btn = st.button("Process Documents", type="primary", use_container_width=True)
            
            if st.session_state.doc_qa_files_processed:
                # Show file count instead of detailed info
                st.success(f"{len(uploaded_files)} documents ready")
                
                # Clear button
                if st.button("Clear", type="secondary", use_container_width=True):
                    if st.session_state.doc_qa_system:
                        st.session_state.doc_qa_system.cleanup()
                    st.session_state.doc_qa_system = None
                    st.session_state.doc_qa_files_processed = False
                    st.session_state.doc_qa_chat_history = []
                    st.rerun()
            
            # Silent processing
            if process_btn:
                if not st.session_state.api_key:
                    st.error("Please set your OpenAI API key first")
                    return
                
                with st.spinner("Processing..."):
                    # Initialize Document QA system silently
                    st.session_state.doc_qa_system = DocumentQARAG(st.session_state.api_key)
                    
                    # Process documents silently (without showing intermediate steps)
                    def silent_log(*args, **kwargs):
                        pass
                    
                    # Temporarily redirect st.info and st.warning to do nothing
                    original_info = st.info
                    original_warning = st.warning
                    st.info = silent_log
                    st.warning = silent_log
                    
                    try:
                        success = st.session_state.doc_qa_system.process_documents(uploaded_files)
                    finally:
                        # Restore the original functions
                        st.info = original_info
                        st.warning = original_warning
                    
                    if success:
                        st.session_state.doc_qa_files_processed = True
                        st.session_state.doc_qa_chat_history = []  # Reset chat history
                        st.rerun()
                    else:
                        st.error("Failed to process documents")
    
    with col2:
        # Main Q&A Interface - Always show the chat UI
        if not st.session_state.doc_qa_files_processed:
            # Show placeholder when no documents are processed yet
            st.info("👈 Upload and process documents to start asking questions")
        else:
            # Chat interface
            st.markdown("#### Ask questions about your documents")
            
            # Display chat history
            for message in st.session_state.doc_qa_chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    # Show sources in expandable section (more compact)
                    if message["role"] == "assistant" and "sources" in message and message["sources"]:
                        with st.expander("View sources", expanded=False):
                            for i, source in enumerate(message["sources"]):
                                st.markdown(f"**Source {i+1}:** {source['source']}")
                                st.markdown(f"*Preview:* {source['content_preview']}")
                                st.markdown("---")
            
            # Chat input for questions
            if question := st.chat_input("Ask a question about your documents..."):
                # Add user message to chat history
                st.session_state.doc_qa_chat_history.append({
                    "role": "user", 
                    "content": question
                })
                
                with st.chat_message("user"):
                    st.markdown(question)
                
                # Generate AI response
                with st.chat_message("assistant"):
                    with st.spinner("Searching..."):
                        result = st.session_state.doc_qa_system.ask_question(question)
                        
                        st.markdown(result["answer"])
                        
                        # Add assistant response to chat history
                        st.session_state.doc_qa_chat_history.append({
                            "role": "assistant",
                            "content": result["answer"],
                            "sources": result["sources"]
                        })
                        
                        # Show sources in expandable section
                        if result["sources"]:
                            with st.expander("View sources", expanded=False):
                                for i, source in enumerate(result["sources"]):
                                    st.markdown(f"**Source {i+1}:** {source['source']}")
                                    st.markdown(f"*Preview:* {source['content_preview']}")
                                    st.markdown("---")
