import json
import os
import glob
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

class KnowledgeBase:
    def __init__(self, data_dir: str = "core/ai/data", model_name: str = "all-MiniLM-L6-v2"):
        self.data_dir = data_dir
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        self.vector_store = None

    def build_index(self):
        documents = []
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

        self.vector_store = FAISS.from_documents(documents, self.embeddings)
        return self.vector_store

    def get_retriever(self, top_k: int = 3):
        if self.vector_store is None:
            self.build_index()
            
        return self.vector_store.as_retriever(search_kwargs={"k": top_k})