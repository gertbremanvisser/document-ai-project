# git-auto.ps1
# Automatisch committen en pushen met datum/tijd in de commit message

# Ga naar de projectroot (optioneel, als je script niet vanuit root draait)
Set-Location $PSScriptRoot

# Genereer commit message met datum/tijd
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
$msg = "Update: $timestamp"

# Voeg alle wijzigingen toe
git add .

# Maak commit
git commit -m $msg

# Push naar remote
git push
