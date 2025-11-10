import os
import fitz  # PyMuPDF
from select_folder import get_main_folder

def analyse_pdfs(folder):
    for file in os.listdir(folder):
        if file.endswith(".pdf"):
            path = os.path.join(folder, file)
            doc = fitz.open(path)
            text = ""
            for page in doc:
                text += page.get_text()

            if text.strip():
                # tekst aanwezig → (TXT)
                new_name = file.replace(".pdf", "(TXT).pdf")
            else:
                # geen tekst → (OCR)
                new_name = file.replace(".pdf", "(OCR).pdf")

            new_path = os.path.join(folder, new_name)
            if not os.path.exists(new_path):
                os.rename(path, new_path)
                print(f"{file} → {new_name}")

if __name__ == "__main__":
    folder = get_main_folder()
    analyse_pdfs(folder)
