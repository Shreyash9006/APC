from PyPDF2 import PdfMerger

merger = PdfMerger()
files=["file1.pdf","file2.pdf","file3.pdf","file4.pdf"]

for file in files:
    merger.append(file)

merger.write("merged.pdf")
merger.close()

print("PDF files merged successfully!")