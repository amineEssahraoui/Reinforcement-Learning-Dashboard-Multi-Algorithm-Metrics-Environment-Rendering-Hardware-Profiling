import sys
import time
from core.ai.knowledge_base import KnowledgeBase
from core.ai.rag_engine import RAGEngine

def main():
    print("Initializing AI...")
    print("Please ensure the Ollama application is running on your PC.")
    print("Loading your JSON files...\n")
    
    start_time = time.time()
    
    try:
        kb = KnowledgeBase(data_dir="core/ai/data")
        retriever = kb.get_retriever(top_k=3)
        print(f"Knowledge base loaded successfully. ({len(kb.vector_store.docstore._dict)} chunks found)")
        
        # Step 2: Launch the engine with Llama 3
        engine = RAGEngine(retriever=retriever, model_name="llama3:8b")
        print(f"RAG Engine connected to Ollama in {time.time() - start_time:.1f} seconds!\n")
        
    except Exception as e:
        print(f"Critical error during loading: {e}")
        sys.exit(1)

    print("="*50)
    print("Chat is open! (Type 'exit' or 'quit' to close)")
    print("="*50)

    # Terminal chat loop
    while True:
        try:
            question = input("\nYou: ")
            if question.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
                
            if not question.strip():
                continue

            print("Llama 3 is thinking...")
            
            # Ask the question to our RAG engine
            response = engine.ask(question)
            
            print(f"\nAI: {response}")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()