from pathlib import Path
import pandas as pd
from src.utils import summarize_text

class CSVEmbedder:
    def __init__(self, input_path):
        self.input_path = input_path

    def process(self):
        df = pd.read_csv(self.input_path)
        
        # Dynamically generate row strings
        lines = df.apply(
            lambda row: ", ".join([f"{col}: {row[col]}" for col in df.columns]), axis=1
        ).tolist()
        print(lines[0]) 
        metadata = self.generate_metadata(df)  # Generate statistical metadata
        lines += metadata.split("\n")
        summary = summarize_text("\n".join(lines[:5]), metadata, self.input_path)  # Summarize only the first few rows
        return lines, summary

    def generate_metadata(self, df):
        """
        Summarizes the statistics of specified columns in a DataFrame.

        Parameters:
        df (pd.DataFrame): The DataFrame containing the data.

        Returns:
        str: A formatted string summarizing the statistics of the specified columns.
        """
        describe_df = df.describe(include='all')
        summaries = []

        for column in df.columns:
            if column in describe_df.columns:
                stats = describe_df[column]
                summary = (
                    f"{column}: count {stats['count']:.0f}, mean {stats['mean']:.2f}, "
                    f"std {stats['std']:.2f}, min {stats['min']:.2f}, "
                    f"25% {stats['25%']:.2f}, 50% {stats['50%']:.2f}, "
                    f"75% {stats['75%']:.2f}, max {stats['max']:.2f}"
                )
                summaries.append(summary)
            else:
                summaries.append(f"{column}: Column not found in DataFrame")

        return "\n".join(summaries)

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