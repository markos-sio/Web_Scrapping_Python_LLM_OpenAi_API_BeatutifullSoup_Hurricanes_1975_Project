import pandas as pd
import requests
from bs4 import BeautifulSoup
import logging
import openai
from typing import Optional, List, Dict

# Set your OpenAI API key here
OPENAI_API_KEY = "my_api_key"
openai.api_key = OPENAI_API_KEY

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

URL = "https://en.wikipedia.org/wiki/1975_Pacific_hurricane_season"

def fetch_html(url: str) -> Optional[bytes]:
    """Fetches the HTML content from the given URL."""
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.content
    except requests.exceptions.Timeout:
        logging.error(f"Error: The request to {url} timed out.")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error: Failed to retrieve page from {url} with ERROR: {e}")
        return None

def parse_html(html_content: bytes) -> BeautifulSoup:
    """Parses the HTML content using BeautifulSoup."""
    return BeautifulSoup(html_content, "html.parser")

def use_llm_for_parsing(text: str) -> str:
    """Uses LLM to parse and extract relevant information from text."""
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            temperature=0.0,  # Set to 0 for consistent results
            messages=[
                {"role": "system", "content": "You are an assistant for extracting hurricane data."},
                {"role": "user", "content": f"Extract details of tropical storms and hurricanes from the 1975 Pacific hurricane season, including their names, start dates, end dates, number of deaths, and a list of areas affected from the following text: {text}. Format the output in a structured way like this: 'Name: [Tropical Storm or Hurricane name or Unnamed Hurricane], Start: [Month day], End: [Month day], Deaths: [number], Affected Areas: [list of areas such as 'Acapulco', 'Socorro Island', 'Pacific Ocean']'. If no area is mentioned, record 'Pacific Ocean'. Do not include data for Tropical Depressions. For dates, omit the year 1975."}
            ]
        )
        message_content = response.choices[0].message.content
        logging.info(f"LLM Output: {message_content}")
        return message_content
    except Exception as e:
        logging.error(f"Error during LLM processing: {e}")
        return None

def extract_information_with_llm(soup: BeautifulSoup) -> str:
    """Extracts relevant information from the HTML using the LLM."""
    # Collect text from <p> tags
    relevant_text = ' '.join([p.text for p in soup.find_all('p')])
    
    # Collect text from <td class="infobox-data"> tags
    infobox_data = ' '.join([td.text for td in soup.find_all('td', class_='infobox-data')])
    
    # Combine both texts
    combined_text = relevant_text + ' ' + infobox_data
    
    return use_llm_for_parsing(combined_text)

def parse_llm_output(llm_output: str) -> List[Dict[str, str]]:
    
    """
    The aim of this function is to parse the output of the LLM (Large Language Model) 
    into a structured format. The function takes the LLM output, which is a string, 
    splits it by lines, and extracts relevant information based on expected patterns. 
    The extracted data is then structured into a list of dictionaries with keys 
    like 'hurricane_storm_name', 'date_start', 'date_end', 'number_of_deaths', 
    and 'list_of_areas_affected'.
    """
    
    structured_data = []
    lines = llm_output.strip().split('\n')

    for line in lines:
        if line.strip():  # Ignore empty lines
            
            # Split by commas to break up the LLM output
            parts = line.split(',')

            if len(parts) >= 5:  # Ensure we have at least the 5 expected fields
                # Extract hurricane name
                name = parts[0].split(':')[1].strip()
                
                # Extract start and end dates
                start_date = parts[1].split(': ')[1].strip()
                end_date = parts[2].split(': ')[1].strip()
                
                # Extract number of deaths
                deaths = parts[3].split(': ')[1].strip()
                
                # Extract affected areas
                affected_areas_str = parts[4].split(': ')[1].strip()
                
                # Handle affected areas: split by comma, and trim spaces
                affected_areas = [area.strip() for area in affected_areas_str.split(',')]
                
                # Append the structured data as a dictionary
                structured_data.append({
                    "hurricane_storm_name": name,
                    "date_start": start_date,
                    "date_end": end_date,
                    "number_of_deaths": deaths,
                    "list_of_areas_affected": affected_areas,  # Always a list
                })

    return structured_data

def create_dataframe(data: List[Dict]) -> pd.DataFrame:
    """Creates a DataFrame from the list of extracted hurricane data."""
    return pd.DataFrame(data)

def save_to_csv(df: pd.DataFrame, filename: str) -> None:
    """
    Saves the DataFrame to a CSV file with proper encoding (UTF-8).
    """
    try:
        df.to_csv(filename, index=False, encoding='utf-8')  # Ensure UTF-8 encoding
        logging.info(f"CSV created successfully: {filename}")
    except Exception as e:
        logging.critical(f"An error occurred while saving the file: {e}")

if __name__ == "__main__":
    # Fetching the HTML content
    logging.info("Fetching HTML content...")
    html_content = fetch_html(URL)

    if html_content:
        logging.info("HTML content fetched successfully.")
        
        # Parsing the HTML content
        logging.info("Parsing HTML content...")
        soup = parse_html(html_content)
        logging.info("HTML content parsed successfully.")
        
        # Extracting information using the LLM
        logging.info("Extracting information using LLM...")
        llm_output = extract_information_with_llm(soup)
        
        
        if not llm_output:
            logging.error("Parsed LLM output is empty or invalid.")
        else:
            logging.info("LLM output extracted successfully.")
            
            # Parsing the LLM output into structured data
            logging.info("Parsing LLM output...")
            structured_data = parse_llm_output(llm_output)
            logging.info("LLM output parsed successfully.")
            
            # Creating a DataFrame from the structured data
            logging.info("Creating DataFrame from structured data...")
            df = create_dataframe(structured_data)
            logging.info("DataFrame created successfully.")
            
            # Saving the DataFrame to CSV
            logging.info("Saving DataFrame to CSV...")
            save_to_csv(df, 'hurricanes_1975.csv')
            logging.info("DataFrame saved to CSV successfully.")

