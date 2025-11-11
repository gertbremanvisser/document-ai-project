# Document AI Project

Dit project automatiseert het analyseren en hernoemen van PDF-bestanden:
- Detecteert of een PDF tekst bevat of OCR nodig heeft
- Voegt `(TXT)` of `(OCR)` toe aan de bestandsnaam
- Logt alle acties in een CSV-bestand voor auditability
- Ondersteunt herhaald draaien zonder dubbele suffixen

---

## 🚀 Workflow

1. **PDF-analyse script (`scripts/pdf_analyse.py`)**
   - Controleert of een PDF tekst bevat
   - Hernoemt bestanden met `(TXT)` of `(OCR)`
   - Schrijft logregels naar `logs/pdf_rename_log.csv`

2. **Audit trail**
   - **Runtime logging**: CSV-bestanden met timestamp, oud pad, nieuw pad, status
   - **Development logging**: GitHub commits met duidelijke berichten

3. **GitHub gebruik**
   - Projectmap staat onder versiebeheer
   - Elke wijziging wordt gecommit en gepusht naar GitHub
   - Issues worden gebruikt voor taken en bugtracking

---

## 📝 Commit-berichten

Gebruik een consistente stijl voor commits:

### Structuur


### Types
- `feat`: nieuwe functionaliteit
- `fix`: bugfix
- `docs`: documentatie
- `refactor`: code herstructurering
- `test`: tests
- `chore`: onderhoud/configuratie

### Voorbeelden
- `feat: Add OCR detection to PDF rename script`
- `fix: Correct error handling in folder selection dialog`
- `docs: Update README with GitHub workflow checklist`
- `refactor: Simplify logging routine for auditability`

---

## 📊 Projectstructuur

document_ai_project/
├── utils/
│   ├── __init__.py          # maakt utils een package
│   ├── config_utils.py      # centrale config functies
│   ├── select_folder.py     # dialoog voor hoofdmap
│   ├── pdf_analyse.py       # analyse van PDF's (fitz)
│   └── pdf_ocr.py           # OCR uitvoeren
├── logs/
│   └── project_setup_log.csv
├── main.py                  # centrale entrypoint
├── .gitignore
├── config.env
└── README.md

---

## ✅ Checklist voor dagelijkse commits

1. `git add .`
2. `git commit -m "feat: Beschrijving van wijziging"`
3. `git push`

---

## 🔒 Auditability

- Bestandsnamen geven status aan: `(TXT)` of `(OCR)`
- CSV-log registreert alle runtime acties
- GitHub commits en issues documenteren alle codewijzigingen
