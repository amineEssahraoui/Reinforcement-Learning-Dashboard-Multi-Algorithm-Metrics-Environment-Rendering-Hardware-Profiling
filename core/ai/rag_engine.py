from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

class RAGEngine:
    def __init__(self, retriever, model_name: str = "llama3"):
        
        self.retriever = retriever
        
        # Connect to the local Ollama server
        self.llm = Ollama(model=model_name)

        # The System Prompt guiding Llama 3's behavior (Now in English!)
        template = """You are an expert AI assistant specializing in Reinforcement Learning.
        You are integrated directly into a professional dashboard.
        Use ONLY the provided context below to answer the user's question.
        If the answer is not contained in the context, simply say that you don't know; do not make up information.
        Be clear, concise, and use a professional and encouraging tone.
        
        Context:
        {context}

        Question: {question}

        Answer:"""

        self.prompt = PromptTemplate.from_template(template)

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        # The RAG Chain (Pipeline)
        self.rag_chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def ask(self, question: str) -> str:
        try:
            response = self.rag_chain.invoke(question)
            return response
        except Exception as e:
            return f"Communication error with the AI. Please verify that Ollama is running. Details: {str(e)}"