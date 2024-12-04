import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS  
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain


load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
#os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
#os.environ['OPEN_AI_API_KEY'] = os.getenv('OPEN_AI_API_KEY')

def extract_using_llm(file) : 
        loader = PyPDFLoader(file)
        doc = loader.load()
        doc_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
        docs = doc_splitter.split_documents(doc)

     
        db = FAISS.from_documents(docs[:5], OllamaEmbeddings())
        print(db)

        
        prompt = """
        Extract {input} from the given document
        {context}
        and arrange the data in the dictionary format 


                            "name": " ",
                        
                            "demographic details" : "name" , "zip" ,"street","city"
                            "materials and quantities (quantity appears immediate after material name example (shingles :41.66))" : " "
                            materials :  
                            "line_no": " ",
                            "quantity": " ",
                            "part_numbers": " ",
                            "product_description": " ",
                            "spell_corrected_product_description": " "
                        
                        put NA if not available
                        materail section to be read from top to bottom , not left to right
                    
        """


        

        
        prompt = ChatPromptTemplate.from_template(prompt)

        
        llm = Ollama(model="llama2")

    
        document_chain = create_stuff_documents_chain(llm, prompt)

        retriever = db.as_retriever()
        chain = create_retrieval_chain(retriever, document_chain)

        res = chain.invoke({"input": "please find customer information(demographic details) and material information  "})      
        return(res['answer'])


