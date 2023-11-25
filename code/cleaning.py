# -*- coding: utf-8 -*-
##### Author: Takumi Shibaike
##### Date: November 21, 2023
##### Revision: V1.0
##### File : cleaning.py

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
i = 17
file_path = '.\\txt\\' + sorted_file_list[i]

with open(file_path, 'r', encoding='utf-8') as file:
    # Read the contents of the file
    file_contents = file.read()

doc = file_contents.replace('\n', '')


# Initialize variables
sections = []
end_number = 1000

# Loop through numbers 1 to 100
for current_number in range(1, end_number + 1):
    # Define the regex pattern for identifying sections
    pattern = re.compile(fr'{current_number}\..*?(?={current_number+1}\.|\Z)', re.DOTALL)

    # Use search to find the first match
    match = pattern.search(doc)

    # Check if a match is found
    if match:
        matched_section = match.group(0).strip()
        sections.append(matched_section)

        # Replace the matched section with an empty string in the original text
        doc = doc.replace(matched_section, "")

# Extract information from the sections list
data = []
doc_id = 'WCPFC'+str(i+1)

for section in sections:
    # Use regular expression to extract the number and content
    match = re.match(r'(\d+)\. (.*)', section)
    
    if match:
        number = int(match.group(1))
        content = match.group(2)
        
        data.append({'Document ID': doc_id, 'Number': number, 'Content': content})

# Create a DataFrame
df = pd.DataFrame(data)

# Display the DataFrame
print(df)

# Write the DataFrame to a CSV file
csv_file_path = ".\\csv\\WCPFC"+str(i+1)+".csv"
df.to_csv(csv_file_path, index=False, encoding='utf-8')