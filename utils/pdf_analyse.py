import os
import fitz  # PyMuPDF

def get_folder():
    # Eerst proberen uit environment
    folder = os.environ.get("MAIN_FOLDER")
    if folder and os.path.isdir(folder):
        return folder
    # Anders uit config.env
    if os.path.exists("config.env"):
        with open("config.env", "r", encoding="utf-8") as f:
            line = f.readline().strip()
            if line.startswith("MAIN_FOLDER="):
                folder = line.split("=", 1)[1]
                if os.path.isdir(folder):
                    return folder
    raise RuntimeError("Geen hoofdmap ingesteld. Draai eerst select_folder.py.")

def analyse_pdfs(folder):
    for file in os.listdir(folder):
        if file.endswith(".pdf") and not ("(TXT)" in file or "(OCR)" in file):
            path = os.path.join(folder, file)
            doc = fitz.open(path)
            text = "".join(page.get_text() for page in doc)

            if text.strip():
                new_name = file.replace(".pdf", "(TXT).pdf")
            else:
                new_name = file.replace(".pdf", "(OCR).pdf")

            new_path = os.path.join(folder, new_name)
            if not os.path.exists(new_path):
                os.rename(path, new_path)
                print(f"{file} → {new_name}")

if __name__ == "__main__":
    folder = get_folder()
    analyse_pdfs(folder)
