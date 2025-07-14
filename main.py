# main.py
import os
from dotenv import load_dotenv
from tabulate import tabulate
import database
import extractor
import agent

def main():
    """Main function to run the data extraction and storage process."""
    print("🚀 Starting the Company Data Extraction Process...")
    
    # 1. Load environment variables and set up the database
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("🔴 Error: OPENAI_API_KEY not found. Please set it in the .env file.")
        return
        
    conn = database.get_db_connection()
    if conn is None:
        return
    database.create_company_table(conn)
    conn.close()

    # 2. Create the extractor chain and the agent
    extractor_chain = extractor.create_extractor_chain()
    agent_executor = agent.create_agent_executor()

    # 3. Read input file and process each paragraph [cite: 32, 50]
    try:
        with open("input.txt", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("🔴 Error: input.txt not found. Please create it with the essay content.")
        return
        
    paragraphs = content.split('\n\n')
    print(f"📄 Found {len(paragraphs)} paragraphs to process.")
    
    for i, para in enumerate(paragraphs):
        if para.strip(): # Ensure paragraph is not empty
            print(f"\n--- Processing Paragraph {i+1} ---")
            try:
                # Use the LCEL chain to extract data
                company_info = extractor_chain.invoke({"text": para})
                
                # If a company was found, use the agent to add it to the DB
                if company_info and company_info.company_name:
                    print(f"🔍 Extracted: {company_info.company_name}")
                    agent.run_agent_to_add_company(agent_executor, company_info)
                else:
                    print("- No company information found in this paragraph.")

            except Exception as e:
                print(f"🔴 Error processing paragraph {i+1}: {e}")

    # 4. Display the final results from the database
    print("\n\n--- ✅ Process Complete ---")
    print("Displaying all companies stored in the database:")
    all_data = database.get_all_companies()
    if isinstance(all_data, list):
        headers = ["ID", "Company Name", "Founded In", "Founded By"]
        print(tabulate(all_data, headers=headers, tablefmt="grid"))
    else:
        print(all_data)


if __name__ == "__main__":
    main()