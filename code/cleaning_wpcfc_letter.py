# -*- coding: utf-8 -*-
##### Author: Takumi Shibaike
##### Date: August 12, 2024
##### Revision: V1.0
##### File : cleaning_linebreak.py

import os
import re
import pandas as pd

os.chdir('C:\\Users\\tshibaik\\OneDrive - Syracuse University\\Desktop\\rfmo')

directory_path = '.\\txt\\coded advocacy letters'

# Ensure the given directory exists
if not os.path.exists(directory_path):
    print(f"Error: Directory '{directory_path}' does not exist.")
else:
    # Get the list of text files in the directory
    text_files = [filename for filename in os.listdir(directory_path) if filename.endswith(".txt")]

    # Sort files in order of meeting number
    sorted_file_list = sorted(text_files, key=lambda filename: int(re.search(r'\d+', filename).group()) if re.search(r'\d+', filename) else 0)

    # Create a list to store the parsed data
    data = []

    # Loop through each file and process it
    for i, filename in enumerate(sorted_file_list):
        file_path = os.path.join(directory_path, filename)
        
        with open(file_path, 'r', encoding='utf-8') as input_file:
            file_content = input_file.read()

        # Clean and split the file content into sections (use '. ' for by sentence)
        file_content = re.sub(r'\n\d+', '', file_content)
        sections = [para.strip() for para in file_content.split('\n \n') if para.strip()]

        # Extract the document ID from the filename
        doc_id = re.findall(r'WCPFC\d+-\d+-OP\d+', filename)
        if doc_id:
            doc_id = doc_id[0]
        else:
            doc_id = f"Unknown-{i}"

        # Loop through each section, assign a section number, and store the data
        for section_num, section_content in enumerate(sections, start=1):
            cleaned_section = re.sub(r'[^a-zA-Z0-9\s]', '', section_content.replace('\n', ' ')).strip()
            # Replace multiple spaces with a single space
            cleaned_section = re.sub(r'\s+', ' ', cleaned_section)
            data.append({
                'doc_id': doc_id,
                'section_num': section_num,
                'section_content': cleaned_section
            })


# Create a Pandas DataFrame
df = pd.DataFrame(data)

# Display the DataFrame
print(df)

# Write the DataFrame to a CSV file
csv_file_path = ".\\csv\\coded_advocacy_letters_2.csv"
df.to_csv(csv_file_path, index=False, encoding='utf-8')