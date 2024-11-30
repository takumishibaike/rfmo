# -*- coding: utf-8 -*-
##### Author: Takumi Shibaike
##### Date: November 21, 2023
##### Revision: V1.3
##### File : cleaning.py

import os
import re
import pandas as pd

# Set the working directory
os.chdir('C:\\Users\\tshibaik\\OneDrive - Syracuse University\\Desktop\\cmm')

# Directory containing the text files
directory_path = '.\\txt\\wcpfc'

# Output directory for CSV files
output_directory = '.\\csv'
os.makedirs(output_directory, exist_ok=True)  # Ensure the output directory exists

# Ensure the given directory exists
if not os.path.exists(directory_path):
    print(f"Error: Directory '{directory_path}' does not exist.")
else:
    # Loop through the files in the directory
    text_files = [filename for filename in os.listdir(directory_path) if filename.endswith(".txt")]

# Sort files in order of meeting number
sorted_file_list = sorted(text_files, key=lambda filename: int(re.search(r'\d+', filename).group()) if re.search(r'\d+', filename) else 0)

# Loop through each file in the sorted list
for file_name in sorted_file_list:
    file_path = os.path.join(directory_path, file_name)

    # Read the contents of the file
    with open(file_path, 'r', encoding='utf-8') as file:
        file_contents = file.read()

    # Clean the document content by removing newlines
    doc = file_contents.replace('\n', '')

    # Determine if the file is "active" or "historical" based on the file name
    status = "active" if "active" in file_name.lower() else "historical"

    # Initialize variables for section extraction
    sections = []
    end_number = 1000  # Maximum number to check for section numbering

#### Change number here if the document cuts off in the middle (likely because the number is not sequential).

    # Extract sections numbered 1 to end_number
    for current_number in range(1, end_number + 1):
        # Regex pattern to identify sections
        pattern = re.compile(fr'{current_number}\..*?(?={current_number+1}\.|\Z)', re.DOTALL)

        # Search for sections matching the pattern
        match = pattern.search(doc)

        # If a match is found, extract and clean the section
        if match:
            matched_section = match.group(0).strip()
            sections.append(matched_section)

            # Remove the matched section from the document to avoid duplication
            doc = doc.replace(matched_section, "")

    # Extract the file name without extension
    file_name_without_extension = os.path.splitext(file_name)[0]

    # Process sections and prepare data for the DataFrame
    data = []
    for section in sections:
        # Use regular expression to extract the section number and content
        match = re.match(r'(\d+)\. (.*)', section)
        if match:
            number = int(match.group(1))  # Section number
            content = match.group(2)  # Section content

            # Append the extracted data
            data.append({
                'CMM': file_name_without_extension,
                'Status': status,
                'Section Number': number,
                'Content': content
            })

    # Create a DataFrame from the extracted data
    df = pd.DataFrame(data)

    # Write the DataFrame to a CSV file
    csv_file_path = os.path.join(output_directory, f"{file_name_without_extension}.csv")
    df.to_csv(csv_file_path, index=False, encoding='utf-8')

    print(f"Processed and saved: {file_name_without_extension}.csv")
