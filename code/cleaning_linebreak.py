# -*- coding: utf-8 -*-
##### Author: Takumi Shibaike
##### Date: November 21, 2023
##### Revision: V1.0
##### File : cleaning_linebreak.py

import os
import re
import pandas as pd

os.chdir('C:\\Users\\tshibaik\\OneDrive - Syracuse University\\Desktop\\wcpfc')

directory_path = '.\\txt'

# Ensure the given directory exists
if not os.path.exists(directory_path):
    print(f"Error: Directory '{directory_path}' does not exist.")
else:
    # Loop through the files in the directory
    text_files = [filename for filename in os.listdir(directory_path) if filename.endswith(".txt")]

# Sort files in order of meeting number
sorted_file_list = sorted(text_files, key=lambda filename: int(re.search(r'\d+', filename).group()) if re.search(r'\d+', filename) else 0)

### Change the i number to find a specific file
# see sorted_file_list
i = 16
file_path = '.\\txt\\' + sorted_file_list[i]

with open(file_path, 'r', encoding='utf-8') as input_file:
    file_content = input_file.read()

# Split the content based on two consecutive line breaks
sections = file_content.split('\n\n')

# Create a list to store the data
data = []

# Process each section
doc_id = 'WCPFC'+str(i+1)
section_id = 1  # Initialize section ID counter

for section_id, section in enumerate(sections, start=1):
    # Remove newline characters and other non-alphanumeric characters
    cleaned_section_content = re.sub(r'[^a-zA-Z0-9\s]', '', section.replace('\n', ' ')).strip()
    # Check if the section meets the length criterion
    if len(cleaned_section_content) >= 60:
        data.append((doc_id, section_id, cleaned_section_content))
        section_id += 1  # Increment section ID only for valid sections


# Create a Pandas DataFrame
df = pd.DataFrame(data, columns=['Document ID', 'Number', 'Content'])

# Display the DataFrame
print(df)

# Write the DataFrame to a CSV file
csv_file_path = ".\\csv\\WCPFC"+str(i+1)+".csv"
df.to_csv(csv_file_path, index=False, encoding='utf-8')