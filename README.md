Process (Updated: November 25, 2023)

1. convert pdfs to txt files ([pdf_to_txt.py](code/pdf_to_txt.py))
2. manually remove attachments and index from txt (top and bottom of the file)
3. parse each file by number ([cleaning.py](code/cleaning.py))
4. some numbers are not properly ordered, manually reorder them on txt file (cleaning.py ends where the number is not ordered properly. extracting the rest of the document as one item, which is very large and noticeable)
5. when documents are not numbered (image numbers or nonexistent), use \n\n as parsing ([cleaning_linebreak.py](code/cleaning_linebreak.py))
6. after cleaning txt files and converting them to csv files, put them together as a large file ([csv_binder.py](code/csv_binder.py))
