import json
import os
import glob
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

class KnowledgeBase:
    def __init__(self, data_dir: str = None, model_name: str = "all-MiniLM-L6-v2"):
        if data_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_dir = os.path.join(current_dir, "data")
        else:
            self.data_dir = data_dir
            
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        self.vector_store = None

    def build_index(self):
        documents = []
        
        # Uses the absolute path to find the json files
        json_files = glob.glob(os.path.join(self.data_dir, "*.json"))
        
        if not json_files:
            raise FileNotFoundError(f"No JSON files found in directory: {self.data_dir}")

        for file_path in json_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                for item in data:
                    text_content = f"Topic: {item.get('topic', '')}\nCategory: {item.get('category', '')}\nDescription: {item.get('content', '')}"
                    
                    metadata = {
                        "topic": item.get("topic", ""), 
                        "category": item.get("category", ""),
                        "source_file": os.path.basename(file_path)
                    }
                    
                    doc = Document(page_content=text_content, metadata=metadata)
                    documents.append(doc)

        # Vectorization and storage in FAISS
        self.vector_store = FAISS.from_documents(documents, self.embeddings)
        return self.vector_store

    def get_retriever(self, top_k: int = 3):
        if self.vector_store is None:
            self.build_index()
            
        return self.vector_store.as_retriever(search_kwargs={"k": top_k})