from langchain.document_loaders import (
    UnstructuredPowerPointLoader, UnstructuredWordDocumentLoader, PyPDFLoader)
import glob
import langchain.text_splitter as text_splitter
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter, CharacterTextSplitter)
import faiss
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
import pickle
from GlobalClasses import GlobalContext
from dotenv import load_dotenv
import os

load_dotenv()
GlobalContext()  # initialize global context

os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_VERSION"] = "2022-12-01"
os.environ["OPENAI_API_BASE"] = GlobalContext.OPENAI_BASE
os.environ["OPENAI_API_KEY"] = GlobalContext.OPENAI_API_KEY


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=0)  # chunk_overlap=30

files = glob.glob("Doc_Store/*.*")

all_docs = []
for p in files:
    if p.lower().endswith(".pptx"):
        loader = UnstructuredPowerPointLoader(p)
        docs = loader.load_and_split(text_splitter)
        print(p)
        print(len(docs))
        all_docs.extend(docs)
    elif p.lower().endswith(".docx"):
        loader = UnstructuredWordDocumentLoader(p)
        docs = loader.load_and_split(text_splitter)
        print(p)
        print(len(docs))
        all_docs.extend(docs)
    elif p.lower().endswith(".pdf"):
        loader = PyPDFLoader(p)
        docs = loader.load_and_split(text_splitter)
        print(p)
        print(len(docs))
        all_docs.extend(docs)


print(len(all_docs))

# Here we create a vector store from the documents and save it to disk.
store = FAISS.from_documents(all_docs, OpenAIEmbeddings(chunk_size=1))

faiss.write_index(store.index, "./Doc_Store/vectorDB.index")
store.index = None
with open("./Doc_Store/vectorDB.pkl", "wb") as f:
    pickle.dump(store, f)
