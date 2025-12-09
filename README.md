# Check_Sudoc_Imports_Sebina
Dans le cadre d'un import quotidien de notices du Sudoc via une passerelle (get_title_data) vers le SIGB Sebina, ce script Python permet de traiter plus rapidement un grand nombre de rapports.
Script permettant d'analyser les alertes (WARN) de type doublon exemplaire (cause manque PPN dans le SIGB : la correspondance déclanche la mise à jour de la notice) > # Détection uniquement des warnings "Code-barres déjà présent"
Il génère à partir d'un dossier source de fichiers .txt un fichier .csv repérant et listant les notices problématiques.

Mode d'emploi :

Spécifier le dossier à analyser : input_files = glob.glob("Nom_de_dossier/*.txt")
Vous pouvez renommer le fichier à créer : output_file = "suspicion_de_doublon.csv"

