@echo off
REM Automatisch committen en pushen met datum/tijd in de commit message

REM Ga naar de projectroot (de map waar dit script staat)
cd /d "%~dp0"

REM Genereer commit message met datum/tijd
for /f "tokens=1-4 delims=:. " %%a in ("%date% %time%") do (
    set commitmsg=Update: %%a-%%b-%%c %%d:%%e
)

REM Voeg alle wijzigingen toe
git add .

REM Maak commit
git commit -m "%commitmsg%"

REM Push naar remote (standaard branch)
git push
