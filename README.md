Process (Updated: August 14, 2024)

Annual meeting summary reports

1. Convert pdf files to txt files ([pdf_to_txt.py](code/pdf_to_txt.py))
2. Manually remove attachments and index from txt (top and bottom of the file)
3. Parse each file by itemized numbers ([cleaning_wcpfc_summary_report.py](code/cleaning_wcpfc_summary_report.py))
4. Some numbers are not properly ordered. Manually reorder them on txt file (cleaning.py ends where any number is not ordered properly, extracting the rest of the document as one item, which is very large and noticeable).
5. When documents are not numbered (image numbers or nonexistent), use \n \n as parsing ([cleaning_linebreak.py](code/cleaning_linebreak.py))
6. After cleaning txt files and converting them to csv files, put them together as a large file ([csv_binder.py](code/csv_binder.py))
7. Run any analysis on the large file ([seededlda_summary_report.r](code/seededlda_summary_report.r)).

Observer letters

1. Convert pdf files to txt files ([pdf_to_txt.py](code/pdf_to_txt.py))
2. Parse each file by line breaks and pout them in a csv file ([cleaning_wpcfc_letter.py](code/code/cleaning_wpcfc_letter.py))
3. Run any analysis on this file ([seededlda_summary_report.r](code/seededlda_letter.r)).

CMMs

1. Convert pdf files to txt files ([pdf_to_txt.py](code/pdf_to_txt.py))
2. Parse each file by line breaks and pout them in a csv file ([cleaning_wcpfc_cmm.py](code/cleaning_wcpfc_cmm.py))
3. Run any analysis on this file ([bertopic_cmm.py](code/bertopic_cmm.py)).
