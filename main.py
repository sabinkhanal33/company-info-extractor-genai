import os
from dotenv import load_dotenv
from langchain_community.document_loaders import UnstructuredURLLoader, Docx2txtLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma as ch
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Optional
from datetime import date
import sqlite3


load_dotenv()
SECRET_KEY = os.getenv('OPENAI_API_KEY')
os.environ["OPENAI_API_KEY"] = SECRET_KEY

# --- DB UTILS ---
def get_db_connection():
    return sqlite3.connect("companies.db")

def create_company_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Company_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            founded_in TEXT NOT NULL,
            founded_by TEXT NOT NULL
        );
    """)
    conn.commit()

def insert_company_data(company_name, founding_date, founders):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        founders_str = ", ".join(founders) if isinstance(founders, list) else str(founders)
        cur.execute(
            """
            INSERT INTO Company_details (company_name, founded_in, founded_by)
            VALUES (?, ?, ?)
            """,
            (company_name, str(founding_date), founders_str)
        )
        conn.commit()
    finally:
        conn.close()

# --- EXTRACTOR ---
class CompanyInfo(BaseModel):
    company_name: Optional[str] = Field(None, description="The name of the company.")
    founders: Optional[List[str]] = Field(None, description="A list of the company's founders.")
    founding_date: Optional[date] = Field(None, description="The founding date of the company.")

def create_extractor_chain():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an expert at extracting company information from text. "
         "Extract the company name, a list of its founders, and its founding date from the user's text. "
         "If founding date information is incomplete, follow these rules strictly: "
         "1. If only the year is provided, default the date to January 1st of that year. \n"
         "2. If the year and month are provided, default the date to the 1st day of that month. \n"
         "If no company information is present in the text, return a result with null values."),
        ("human", "{text}")
    ])
    extractor = prompt | llm.with_structured_output(CompanyInfo)
    return extractor

# --- MAIN PIPELINE ---
def main():
    # DB setup
    conn = get_db_connection()
    create_company_table(conn)
    conn.close()

    # Only use assignment_two/input.txt
    input_txt = "input.txt"
    documents = []
    try:
        with open(input_txt, "r") as f:
            text = f.read()
            documents.append(text)
    except Exception as e:
        print(f"Text load error: {e}")

    if not documents:
        print("No documents loaded. Exiting.")
        return

    # Chunking
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.create_documents(documents)
    print(f"Total chunks: {len(chunks)}")

    # Extraction
    extractor = create_extractor_chain()
    extracted_companies = []
    for chunk in chunks:
        text = chunk.page_content if hasattr(chunk, 'page_content') else str(chunk)
        result = extractor.invoke({"text": text})
        if result.company_name and result.founders and result.founding_date:
            insert_company_data(result.company_name, result.founding_date, result.founders)
            extracted_companies.append(result)

    print(f"Extracted and stored {len(extracted_companies)} companies.")
    for c in extracted_companies:
        print(f"- {c.company_name} (Founded: {c.founding_date}, Founders: {', '.join(c.founders)})")

if __name__ == "__main__":
    main()
