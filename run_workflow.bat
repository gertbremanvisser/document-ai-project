@echo off
REM === Workflow voor PDF-analyse en OCR ===

REM 1. Controleer of MAIN_FOLDER al bestaat
if defined MAIN_FOLDER (
    echo MAIN_FOLDER is al ingesteld op: %MAIN_FOLDER%
) else (
    echo MAIN_FOLDER nog niet ingesteld, start select_folder.py...
    python utils\select_folder.py
    REM config.env wordt door select_folder.py geschreven
    for /f "tokens=2 delims==" %%a in (config.env) do set MAIN_FOLDER=%%a
    echo MAIN_FOLDER ingesteld op: %MAIN_FOLDER%
)

REM 2. Analyse uitvoeren
echo Start analyse...
python utils\pdf_analyse.py

REM 3. OCR uitvoeren
echo Start OCR...
python utils\pdf_ocr.py

echo Workflow afgerond.
pause
