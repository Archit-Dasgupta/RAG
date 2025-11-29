import os
from pypdf import PdfReader

def check_pdf_text():
    docs_folder = "documents"
    if not os.path.exists(docs_folder):
        print("Documents folder not found.")
        return

    files = [f for f in os.listdir(docs_folder) if f.lower().endswith('.pdf')]
    if not files:
        print("No PDF files found.")
        return

    for filename in files:
        filepath = os.path.join(docs_folder, filename)
        print(f"--- Checking {filename} ---")
        try:
            with open(filepath, 'rb') as f:
                pdf = PdfReader(f)
                text = ""
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                        print(f"Page {i+1} extracted {len(page_text)} characters.")
                    else:
                        print(f"Page {i+1} is empty or could not be read.")
                
                print("\n--- First 500 characters ---")
                print(text[:500])
                print("\n--- Last 500 characters ---")
                print(text[-500:])
        except Exception as e:
            print(f"Error reading {filename}: {e}")

if __name__ == "__main__":
    check_pdf_text()
