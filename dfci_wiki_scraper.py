import requests
from bs4 import BeautifulSoup
import csv
import os
import re
import argparse
from typing import List, Optional

def fetch_page_content(url: str) -> Optional[BeautifulSoup]:
    """Fetch the content of the page and return a BeautifulSoup object."""
    response = requests.get(url, verify=False)  # verify=False to ignore SSL certificate validation
    if response.status_code == 200:
        return BeautifulSoup(response.content, 'html.parser')
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

def clean_title(title: str) -> str:
    """Clean the title to create a valid filename prefix."""
    return re.sub(r'\W+', '_', title)

def write_text_content(title: str, content: BeautifulSoup, filename: str) -> None:
    """Write the title, main content, and hyperlinks to a text file."""
    with open(filename, 'w') as txtfile:
        # Write the title
        txtfile.write(f"Title: {title}\n\n")
        
        # Extract and write all paragraphs, skipping those within tables
        paragraphs = content.find_all('p')
        for para in paragraphs:
            # Check if the paragraph is inside a table or table-related tag
            if para.find_parent(['table', 'tr', 'td']):
                continue  # Skip this paragraph
            txtfile.write(para.text + "\n")
        
        # Extract and write the list of hyperlinks
        links_list = content.find('ul', {'class': 'childpages-macro'})
        if links_list:
            links = links_list.find_all('a')
            txtfile.write("\nList of hyperlinks:\n")
            for link in links:
                href = link.get('href')
                text = link.text
                txtfile.write(f"{text}: {href}\n")
        else:
            print("No hyperlinks found.\n")

def write_tables_to_csv(content: BeautifulSoup, title_prefix: str, output_folder: str) -> None:
    """Extract all tables and save them as CSV files."""
    tables = content.find_all('table', {'class': 'wrapped confluenceTable'})
    if tables:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            
            # Open a CSV file to write the table data
            csv_filename = os.path.join(output_folder, f'{title_prefix}_table_{i+1}.csv')
            with open(csv_filename, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                
                for row in rows:
                    # Check if the row contains header cells
                    headers = row.find_all('th')
                    if headers:
                        header_texts = [header.get_text(strip=True) for header in headers]
                        csvwriter.writerow(header_texts)
                    else:
                        cells = row.find_all('td')
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        csvwriter.writerow(cell_texts)
            print(f"Table {i+1} content has been written to '{csv_filename}'.")
    else:
        print("No tables found.")

def process_url(url: str, output_folder: str) -> None:
    """Process a single URL."""
    soup = fetch_page_content(url)
    if soup:
        # Find the page title
        title = soup.find('title').text
        print(f"Processing page: {title}")
        
        # Clean the title to create a valid filename prefix
        title_prefix = clean_title(title)
        
        # Create a text file to write the title, content, and hyperlinks
        txt_filename = os.path.join(output_folder, f'{title_prefix}.txt')
        content = soup.find('div', {'id': 'main-content', 'class': 'wiki-content'})
        
        if content:
            write_text_content(title, content, txt_filename)
            write_tables_to_csv(content, title_prefix, output_folder)
            print(f"Text content has been written to '{txt_filename}'.")
        else:
            print("Main content not found.")
    else:
        print("Failed to retrieve the page content.")

def main(url: Optional[str], file: Optional[str], output_folder: str) -> None:
    """Main function to orchestrate the scraping and writing process."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if url:
        process_url(url, output_folder)
    elif file:
        with open(file, 'r') as f:
            urls = f.read().splitlines()
            for url in urls:
                process_url(url, output_folder)
    else:
        print("No URL or file provided.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape DFCI wiki pages and save content.")
    parser.add_argument('-u', '--url', type=str, help="The URL of the page to scrape.")
    parser.add_argument('-f', '--file', type=str, help="A file containing a list of URLs to scrape.")
    parser.add_argument('-o', '--output', type=str, required=True, help="The output folder to save the files.")
    args = parser.parse_args()
    
    main(args.url, args.file, args.output)