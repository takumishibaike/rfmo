# -*- coding: utf-8 -*-
##### Author: Takumi Shibaike
##### Date: November 21, 2023
##### Revision: V1.0
##### File : ocr.py

import os
import fitz  # PyMuPDF
from PIL import Image
import easyocr

# PDF to text conversion
pdf_path = '.\\pdf\\WCPFC17 Summary Report _final_for_ocr.pdf'

# Open the PDF file
pdf_document = fitz.open(pdf_path)

# Initialize an empty string to store the text
text = ""

# Set up the easyocr reader
reader = easyocr.Reader(['en'])  # You can specify the language(s) you expect in the text

# Iterate through each page in the PDF
for page_number in range(pdf_document.page_count):
    # Get the page
    page = pdf_document[page_number]

    # Convert the page to an image
    pix = page.get_pixmap()
    image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).convert("RGB")

    # Save the image to a temporary file
    temp_image_path = f"temp_page_{page_number + 1}.png"
    image.save(temp_image_path)

    # Use OCR to extract text from the image
    result = reader.readtext(temp_image_path)

    # Extract text from the OCR result
    page_text = ' '.join([entry[1] for entry in result])

    # Append the extracted text to the result
    text += page_text

    # Delete the temporary image file
    # Note: You may want to remove this line if you want to keep the image files
    # after the text has been extracted
    os.remove(temp_image_path)

# Close the PDF document
pdf_document.close()

# Save the extracted text to a text file
output_file_path = 'output.txt'
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    output_file.write(text)