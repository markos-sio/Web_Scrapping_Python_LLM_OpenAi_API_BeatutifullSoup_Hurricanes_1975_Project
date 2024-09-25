Overview
This project is designed to extract data from the Wikipedia page for the 1975 Pacific Hurricane Season and structure the relevant information about tropical storms and hurricanes into a CSV file. It leverages web scraping, Natural Language Processing (NLP), and OpenAI's GPT-4 API to identify storm data such as storm names, dates, number of deaths, and affected areas.

Features
Web scraping: Fetches and parses HTML content from a Wikipedia page.
NLP with GPT-4: Uses OpenAI's GPT-4 to interpret and extract structured information about the hurricanes.
Data handling: Converts extracted hurricane information into a structured format and exports it to a CSV file.
Technologies Used
Python 3.10.9
pandas for data manipulation
requests for fetching the HTML content
BeautifulSoup from bs4 for parsing HTML
openai for interacting with OpenAI's GPT-4 API
logging for logging events
