import re
import csv
import glob
import os

# ============================================================
#  DÉTECTION AUTOMATIQUE DE L’ENCODAGE
# ============================================================

try:
    import chardet
    HAVE_CHARDET = True
except ImportError:
    HAVE_CHARDET = False

FALLBACK_ENCODINGS = ["utf-8", "utf-8-sig", "cp1252", "iso-8859-1"]

def detect_encoding_bytes(bts):
    """Utilise chardet si disponible pour deviner l’encodage."""
    if HAVE_CHARDET:
        try:
            res = chardet.detect(bts)
            enc = res.get("encoding")
            conf = res.get("confidence", 0)
            if enc and conf >= 0.5:
                return enc
        except Exception:
            pass
    return None

def open_with_fallback(path):
    """Ouvre un fichier texte en essayant plusieurs encodages."""
    with open(path, "rb") as bf:
        sample = bf.read(4096)

    tried = []
    enc = detect_encoding_bytes(sample)

    # Essai avec l’encodage détecté
    if enc:
        tried.append(enc)
        try:
            f = open(path, "r", encoding=enc, errors="strict")
            return f, enc, tried
        except Exception:
            pass

    # Essai des encodages fallback
    for e in FALLBACK_ENCODINGS:
        if e in tried:
            continue
        try:
            f = open(path, "r", encoding=e, errors="strict")
            return f, e, tried + [e]
        except Exception:
            tried.append(e)

    # Dernier recours
    f = open(path, "r", encoding="utf-8", errors="replace")
    return f, "utf-8 (replace)", tried + ["utf-8 (replace)"]


# ============================================================
#  LISTE DES WARN À DÉTECTER
# ============================================================

WARN_PATTERNS = [

    # -------- WARN 1 : Code-barres déjà présent --------
    {
        "name": "code_barres_deja_present",
        "regex": re.compile(
            r"WARN>.*Titre\s*:\s*(\S+).*Code-barres\s*(\d+).*déjà présent",
            re.IGNORECASE
        ),
        "extract_title": False  # Titre et code-barres déjà capturés
    },

    # -------- WARN 2 : Trouvée similaire à … cause: DIA107 --------
    {
        "name": "similaire_DIA107",
        "regex": re.compile(
            r"Not\.?\s+liée\s+\(cd=(\S+)\)\s+Trouvée?\s+similaire\s+à\s+(\S+)\s+cause\s*:\s*(DIA107)",
            re.IGNORECASE
        ),
        "extract_title": True   # On tentera d’extraire le titre si présent
    }
]

# Fallback générique pour retrouver "Titre : xxx" dans une ligne
REGEX_TITRE = re.compile(r"Titre\s*:\s*(\S+)", re.IGNORECASE)

# ============================================================
#  TRAITEMENT MULTI-FICHIERS
# ============================================================

INPUT_GLOB = "Rapports imports Sudoc 2025/*.txt"
OUTPUT_FILE = "warnings_multitype.csv"

rows = []
input_files = sorted(glob.glob(INPUT_GLOB))

if not input_files:
    print(f"Aucun fichier trouvé pour : {INPUT_GLOB}")
else:
    for input_file in input_files:

        print(f"\n--- Traitement : {input_file} ---")
        fobj, used_enc, tried = open_with_fallback(input_file)
        print(f"Encodage retenu : {used_enc} (tests : {', '.join(tried)})")

        with fobj:
            for num_ligne, line in enumerate(fobj, start=1):
                line = line.strip()

                # On teste chaque WARN
                for warn in WARN_PATTERNS:
                    match = warn["regex"].search(line)
                    if not match:
                        continue

                    warn_name = warn["name"]

                    # Extraction du titre
                    if warn["extract_title"]:
                        m_titre = REGEX_TITRE.search(line)
                        titre = m_titre.group(1) if m_titre else ""
                    else:
                        titre = match.group(1) if match.groups() else ""

                    # Extraction spécifique selon le type de WARN
                    code_barres = ""
                    notice_liee = ""
                    similaire = ""
                    cause = ""

                    if warn_name == "code_barres_deja_present":
                        # groupes : titre, code_barres
                        code_barres = match.group(2)

                    elif warn_name == "similaire_DIA107":
                        # groupes : notice liée, similaire, cause
                        notice_liee = match.group(1)
                        similaire = match.group(2)
                        cause = match.group(3)

                    # On enregistre la ligne
                    rows.append({
                        "type_warn": warn_name,
                        "fichier": os.path.basename(input_file),
                        "titre": titre,
                        "code_barres": code_barres,
                        "notice_liee": notice_liee,
                        "similaire": similaire,
                        "cause": cause,
                        "ligne_fichier": num_ligne,
                        "message_complet": line
                    })

                    break  # On arrête au premier WARN détecté sur cette ligne


# ============================================================
#  EXPORT CSV
# ============================================================

with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=[
        "type_warn",
        "fichier",
        "titre",
        "code_barres",
        "notice_liee",
        "similaire",
        "cause",
        "ligne_fichier",
        "message_complet"
    ])
    writer.writeheader()
    writer.writerows(rows)

print(f"\nCSV généré : {OUTPUT_FILE} ({len(rows)} lignes de WARN détectées)")
