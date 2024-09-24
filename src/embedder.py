from pathlib import Path
import pandas as pd
from src.azure_client import client, completion_model

class CSVEmbedder:
    def __init__(self, input_path):
        self.input_path = input_path
        self.azure_openai_client = client
        self.model = completion_model

    def process(self):
        df = pd.read_csv(self.input_path)
        
        if df.empty:
            print("The input CSV is empty.")
            return [], "No data to process."
        
        # Flatten each row dynamically
        lines = df.apply(self.flatten_row, axis=1).tolist()
        
        # Print first flattened row (for debugging purposes)
        # print(lines[0]) 
        
        # Call the new function to get schema and summary using Azure OpenAI
        schema_and_summary = self.generate_schema_and_summary(df)
        # print(schema_and_summary)
        # sys.exit(0)
        lines.append(schema_and_summary)
        
        # Summarize only the first few rows
        # summary = summarize_text("\n".join(lines[:5]), schema_and_summary, self.input_path)  
        return lines, schema_and_summary 

    def flatten_row(self, row):
        """
        Flattens a row of the DataFrame by concatenating column names with their values.

        Parameters:
        row (pd.Series): A single row of the DataFrame.

        Returns:
        str: A flattened string representing the row.
        """
        return ", ".join([f"{col}: {row[col]}" for col in row.index])

    def generate_schema_and_summary(self, df, n_rows=50):
        """
        Calls the completion API to generate a schema and summary for the DataFrame.
        """
        file_name = Path(self.input_path).stem
        # Prepare the schema: a list of column names and their data types
        schema = [f"{col}: {df[col].dtype}" for col in df.columns]
        schema_str = "\n".join(schema)

        # Check if table has fewer than 30 rows and adjust number of rows for summary
        if len(df) <= n_rows:
            sample_rows = df.to_string(index=False)  # Use the entire table if rows < 50
        else:
            sample_rows = df.head(n_rows).to_string(index=False)  # Use head part if more than 30 rows

        # Prepare the question for GPT
        question = "Can you summarize the following table schema and provide a concise overview of the data?"

        # Prepare the context for the GPT model (schema and sample data)
        context = f"Table Schema:\n{schema_str}\n\nSample Data:\n{sample_rows}"

        try:
            print("Generating table schema and summary...")
            # Call the Azure OpenAI completion API to generate the schema and summary
            response = self.azure_openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI with expertise in data analysis and summarization."},
                    {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
                ],
                max_tokens=2000
            )

            # Extract the response text
            schema_and_summary = f"Table Name: {file_name}\n" + response.choices[0].message.content.strip()
        except Exception as e:
            raise e
            # print(f"Error generating schema and summary: {e}")
            # print(f"Context passed to API: {context}")
            # schema_and_summary = "Error generating schema and summary."

        return schema_and_summary

class TXTEmbedder:
    def __init__(self, input_path):
        self.input_path = input_path

    def process(self):
        file_name = Path(self.input_path).stem
        with open(self.input_path, 'r') as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]
        # Concatenate with file name
        summary = f"file name: {file_name}"  # No summary for TXT files
        return lines, summary