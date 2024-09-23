import requests
from bs4 import BeautifulSoup
import csv
import os
import re
import argparse
import urllib3
from typing import List, Optional

# Suppress only the single InsecureRequestWarning from urllib3 needed for this script
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_page_content(url: str) -> Optional[BeautifulSoup]:
    """Fetch the content of the page and return a BeautifulSoup object."""
    try:
        response = requests.get(url, verify=False)  # verify=False to ignore SSL certificate validation
        if response.status_code == 200:
            return BeautifulSoup(response.content, 'html.parser')
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"An error occurred while fetching the page: {e}")
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
            txtfile.write("No hyperlinks found.\n")

def handle_rowspan(rowspan_cells: dict, row_idx: int, col_idx: int, cell_text: str, rowspan: int) -> None:
    """Handle cells with rowspan by storing their content in the rowspan_cells dictionary."""
    for r in range(1, rowspan):
        if row_idx + r not in rowspan_cells:
            rowspan_cells[row_idx + r] = {}
        if col_idx not in rowspan_cells[row_idx + r]:
            rowspan_cells[row_idx + r][col_idx] = []
        rowspan_cells[row_idx + r][col_idx].append(cell_text)

def extract_table_content(table: BeautifulSoup, is_nested: bool = False) -> List[List[str]]:
    """Extract the content of a table, including nested tables, and format them appropriately."""
    rows = table.find_all('tr')
    table_content = []
    rowspan_cells = {}

    for row_idx, row in enumerate(rows):
        # Avoid processing the row if it's part of a nested table
        if row.find_parent('table') != table and not is_nested:
            continue

        cells = row.find_all(['th', 'td'])
        cell_texts = []
        col_idx = 0

        while col_idx < len(cells):
            cell = cells[col_idx]
            rowspan = int(cell.get('rowspan', 1))
            colspan = int(cell.get('colspan', 1))
            cell_text = cell.get_text(strip=True)

            # Handle nested tables
            nested_table = cell.find('table')
            if nested_table:
                nested_table_content = extract_nested_table_content(nested_table)
                cell_text = f"Nested Table: {nested_table_content}"

            # Handle rowspan
            if rowspan > 1:
                handle_rowspan(rowspan_cells, row_idx, col_idx, cell_text, rowspan)

            # Handle colspan
            for c in range(colspan):
                cell_texts.append(cell_text)
                col_idx += 1

        # Add any cells from previous rowspans
        if row_idx in rowspan_cells:
            for col, texts in sorted(rowspan_cells[row_idx].items()):
                merged_text = ";".join(texts)
                cell_texts.insert(col, merged_text)

        # Only add the row to table content if it's not a nested table
        if not is_nested:
            table_content.append(cell_texts)

    return table_content

def extract_nested_table_content(nested_table: BeautifulSoup) -> str:
    """Extract the content of a nested table and format it as a string."""
    nested_content = []
    
    # Loop over all rows in the nested table
    for row in nested_table.find_all('tr'):
        # Find all cells in the nested table row
        cells = row.find_all(['th', 'td'])
        # Join the contents of the cells with commas
        nested_row_content = ",".join(cell.get_text(strip=True) for cell in cells)
        # Add the row to the nested content
        nested_content.append(nested_row_content)
    
    # Return the formatted nested table content
    return "\\n".join(nested_content)

def merge_rows(table_content: List[List[str]]) -> List[List[str]]:
    """Merge rows with the same values in all columns except the last one."""
    if not table_content:
        return []

    merged_content = [table_content[0]]  # Start with the header row

    for i in range(1, len(table_content)):
        current_row = table_content[i]
        last_merged_row = merged_content[-1]

        # Check if all columns except the last one are the same
        if current_row[:-1] == last_merged_row[:-1]:
            # Merge the last column values
            last_merged_row[-1] += ";" + current_row[-1]
        else:
            # Add the current row as a new row
            merged_content.append(current_row)

    return merged_content

def write_tables_to_csv(content: BeautifulSoup, title_prefix: str, output_folder: str) -> None:
    """Extract all tables and save them as CSV files."""
    tables = content.find_all('table', {'class': ['confluenceTable', 'wrapped confluenceTable', 'wrapped fixed-table confluenceTable']})
    if tables:
        tables_folder = os.path.join(output_folder, 'tables')
        if not os.path.exists(tables_folder):
            os.makedirs(tables_folder)
        
        for i, table in enumerate(tables):
            # Skip tables inside other tables (nested tables)
            if table.find_parent(['td', 'th']):
                continue

            # Extract table content (handling nested tables within cells)
            table_content = extract_table_content(table)
            table_content = merge_rows(table_content)
            csv_filename = os.path.join(tables_folder, f'{title_prefix}_table_{i+1}.csv')
            
            # Write the table content to a CSV file
            with open(csv_filename, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerows(table_content)
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
                if url:
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