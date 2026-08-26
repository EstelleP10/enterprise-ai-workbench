from pypdf import PdfReader

pdf_path = "knowledge_base/raw/报销制度.pdf"

reader = PdfReader(pdf_path)

for page in reader.pages:
    text = page.extract_text()
    print(text)