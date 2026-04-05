from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / ".." / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Création des répertoires s'ils n'existent pas
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# URLs des données
URLS = {
    "candidats_stat": "https://static.data.gouv.fr/resources/elections-municipales-2020-liste-des-candidats-elus-au-t1-et-liste-des-communes-entierement-pourvues/20200617-160846/maires-au-17-06-2020-vf.xlsx",
    "ville_stat": 'https://object.files.data.gouv.fr/data-pipeline-open/elections/general_results.csv'
}

# Options pour les requêtes HTTP
REQUEST_OPTIONS = {
}

# Noms des fichiers de données brutes
RAW_DATA_FILES = {
    "nuances": RAW_DATA_DIR / "nuances.csv",
    "livre-des-listes-et-candidats": RAW_DATA_DIR / "livre-des-listes-et-candidats.xlsx",
    "candidats_stat": RAW_DATA_DIR / "elus-maires-mai.csv",
    'stat_ville_histo': RAW_DATA_DIR / "DS_RP_SERIE_HISTORIQUE_2022_data.csv",
    'stat_ville_histo_metadata': RAW_DATA_DIR / "DS_RP_SERIE_HISTORIQUE_2022_metadata.csv",
    "2001_res": RAW_DATA_DIR / "Resultat/2001_BVot_T1T2.xls",
    "2008_res": RAW_DATA_DIR / "Resultat/2008_BVot_T1T2.txt",
    "2014_res": RAW_DATA_DIR / "Resultat/2014_BVot_T1T2.txt",
    "2020_res_tour1": RAW_DATA_DIR / "Resultat/2020-05-18-resultats-par-niveau-burvot-t1-france-entiere.xlsx",
    "2020_res_tour2": RAW_DATA_DIR / "Resultat/resultats-par-niveau-burvot-t2-france-entiere.xlsx",
}

PROCESSED_DATA_FILES = {
}
