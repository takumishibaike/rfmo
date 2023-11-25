# -*- coding: utf-8 -*-
##### Author: Takumi Shibaike
##### Date: November 21, 2023
##### Revision: V1.0
##### File : pdf_to_txt.py

import os
import fitz 

os.chdir('C:\\Users\\tshibaik\\OneDrive - Syracuse University\\Desktop\\wcpfc')


# Replace 'pdf_directory' with the path to the directory containing your PDF files
pdf_directory = '.\\pdf'

# Replace 'output_directory' with the path to the directory where you want to save the text files
output_directory = '.\\txt'

# Ensure the output directory exists, create it if not
os.makedirs(output_directory, exist_ok=True)

# Loop through all files in the PDF directory
for filename in os.listdir(pdf_directory):
    if filename.endswith('.pdf'):  # Check if the file is a PDF file
        pdf_path = os.path.join(pdf_directory, filename)
        
        # Generate corresponding output text file name by changing the extension to '.txt'
        txt_filename = os.path.splitext(filename)[0] + '.txt'
        txt_path = os.path.join(output_directory, txt_filename)

        # Open the PDF file
        doc = fitz.open(pdf_path)

        # Open the text file for writing
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            # Iterate through each page of the PDF
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text = page.get_text()
                
                # Write the text to the text file
                txt_file.write(text)

        # Close the PDF file
        doc.close()