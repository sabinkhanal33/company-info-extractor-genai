# extractor.py
from datetime import date
from typing import List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI

# Define the structured output model using Pydantic [cite: 36]
class CompanyInfo(BaseModel):
    """Structured information about a company."""
    company_name: Optional[str] = Field(None, description="The name of the company.")
    founders: Optional[List[str]] = Field(None, description="A list of the company's founders.")
    founding_date: Optional[date] = Field(None, description="The founding date of the company.")

# Create the extractor using LCEL (LangChain Expression Language)
def create_extractor_chain():
    """Creates an LCEL chain to extract structured company data from text."""
    # Initialize the OpenAI model
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Define the extraction prompt
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert at extracting company information from text. "
            "Extract the company name, a list of its founders, and its founding date from the user's text. "
            "If founding date information is incomplete, follow these rules strictly: "
            "1. If only the year is provided, default the date to January 1st of that year. \n"
            "2. If the year and month are provided, default the date to the 1st day of that month. \n"
            "If no company information is present in the text, return a result with null values."
        ),
        (
            "human",
            "{text}"
        )
    ])
    
    # Create the LCEL chain with structured output 
    extractor = prompt | llm.with_structured_output(CompanyInfo)
    return extractor