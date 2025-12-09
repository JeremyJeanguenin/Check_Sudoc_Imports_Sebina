import re
import csv
import glob
import os

# Tous les fichiers .txt du dossier
input_files = glob.glob("Rapports imports Sudoc 2025/*.txt")

output_file = "codebarres_deja_present.csv"

# Détection uniquement des warnings "Code-barres déjà présent"
regex_cb = re.compile(
    r"WARN>.*Titre\s*:\s*(\S+).*Code-barres\s*(\d+).*déjà présent",
    re.IGNORECASE
)

rows = []

for input_file in input_files:
    print(f"Traitement de : {input_file}")

    with open(input_file, "r", encoding="utf-8") as f:
        for num_ligne, line in enumerate(f, start=1):
            line = line.strip()

            m = regex_cb.search(line)
            if m:
                titre = m.group(1)
                code_barres = m.group(2)

                rows.append({
                    "fichier": os.path.basename(input_file),
                    "titre": titre,
                    "code_barres": code_barres,
                    "ligne_fichier": num_ligne,
                    "message_complet": line
                })

# Export CSV
with open(output_file, "w", encoding="utf-8", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=[
        "fichier", "titre", "code_barres", "ligne_fichier", "message_complet"
    ])
    writer.writeheader()
    writer.writerows(rows)

print(f"CSV généré : {output_file} ({len(rows)} warnings trouvés)")
