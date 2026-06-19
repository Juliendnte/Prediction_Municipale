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
    "2026_res_tour1": RAW_DATA_DIR / "Resultat/2026_Tour1.csv",
    "2026_res_tour2": RAW_DATA_DIR / "Resultat/2026_Tour2.csv",
    "INSEE_2007_Fam": RAW_DATA_DIR / "INSEE/2007/Couples - Familles - Ménages 2007/BTX_TD_FAM4_2007.xls",
    "INSEE_2007_Men": RAW_DATA_DIR / "INSEE/2007/Couples - Familles - Ménages 2007/BTX_TD_MEN1_2007.xls",
    "INSEE_2007_Dip": RAW_DATA_DIR / "INSEE/2007/Diplôme - Formation - Mobilités scolaires 2007/BTX_TD_FOR2_2007.xls",
    "INSEE_2007_Nat": RAW_DATA_DIR / "INSEE/2007/Immigrés 2007/BTX_TD_NAT1_2007.xls",
    "INSEE_2007_Nat2": RAW_DATA_DIR / "INSEE/2007/Immigrés 2007/BTX_TD_NAT3_2007.xls",
    "INSEE_2007_Img": RAW_DATA_DIR / "INSEE/2007/Immigrés 2007/BTX_TD_IMG1_2007.xls",
    "INSEE_2007_Log": RAW_DATA_DIR / "INSEE/2007/Logements - Migrations résidentielles 2007/BTX_TD_PRINC14_2007.xls",
    "INSEE_2007_Emp": RAW_DATA_DIR / "INSEE/2007/Population active - Emploi - Chômage 2007/BTX_TD_EMP3_2007.xls",
    "INSEE_2007_Pop": RAW_DATA_DIR / "INSEE/2007/Évolution et structure de la population 2007/BTX_TD_POP5_2007.xls",
    "INSEE_2007_Pop2": RAW_DATA_DIR / "INSEE/2007/Évolution et structure de la population 2007/BTX_TD_POP6_2007.xls",
    "INSEE_2013_Fam": RAW_DATA_DIR / "INSEE/2013/Couples - Familles - Ménages/BTX_TD_FAM4_2013.xls",
    "INSEE_2013_Men": RAW_DATA_DIR / "INSEE/2013/Couples - Familles - Ménages/BTX_TD_MEN1_2013.xls",
    "INSEE_2013_Dip": RAW_DATA_DIR / "INSEE/2013/Diplôme - Formation - Mobilités scolaires/BTX_TD_FOR2_2013.xls",
    "INSEE_2013_Nat": RAW_DATA_DIR / "INSEE/2013/Immigrés/BTX_TD_NAT1_2013.xls",
    "INSEE_2013_Nat2": RAW_DATA_DIR / "INSEE/2013/Immigrés/BTX_TD_NAT3_2013.xls",
    "INSEE_2013_Img": RAW_DATA_DIR / "INSEE/2013/Immigrés/BTX_TD_IMG1_2013.xls",
    "INSEE_2013_Log": RAW_DATA_DIR / "INSEE/2013/Logements - Migrations résidentielles/BTX_TD_PRINC14_2013.xls",
    "INSEE_2013_Emp": RAW_DATA_DIR / "INSEE/2013/Population active - Emploi - Chômage/BTX_TD_EMP3_2013.xls",
    "INSEE_2013_Pop": RAW_DATA_DIR / "INSEE/2013/Évolution et structure de la population/BTX_TD_POP5_2013.xls",
    "INSEE_2013_Pop2": RAW_DATA_DIR / "INSEE/2013/Évolution et structure de la population/BTX_TD_POP6_2013.xls",
    "INSEE_2019_Fam": RAW_DATA_DIR / "INSEE/2019/Couples - Familles - Ménages/BTX_TD_FAM4_2019.xlsx",
    "INSEE_2019_Men": RAW_DATA_DIR / "INSEE/2019/Couples - Familles - Ménages/BTX_TD_MEN1_2019.xlsx",
    "INSEE_2019_Dip": RAW_DATA_DIR / "INSEE/2019/Diplômes - Formation - Mobilités scolaires/BTX_TD_FOR2_2019.xlsx",
    "INSEE_2019_Nat": RAW_DATA_DIR / "INSEE/2019/Étrangers - Immigrés/BTX_TD_NAT1_2019.xlsx",
    "INSEE_2019_Nat2": RAW_DATA_DIR / "INSEE/2019/Étrangers - Immigrés/BTX_TD_NAT3_2019.xlsx",
    "INSEE_2019_Img": RAW_DATA_DIR / "INSEE/2019/Étrangers - Immigrés/BTX_TD_IMG1_2019.xlsx",
    "INSEE_2019_Log": RAW_DATA_DIR / "INSEE/2019/Logements/BTX_TD_PRINC14_2019.xlsx",
    "INSEE_2019_Emp": RAW_DATA_DIR / "INSEE/2019/Population active - Emploi - Chômage/BTX_TD_EMP3_2019.xlsx",
    "INSEE_2019_Pop": RAW_DATA_DIR / "INSEE/2019/Évolution et structure de la population/BTX_TD_POP5_2019.xlsx",
    "INSEE_2019_Pop2": RAW_DATA_DIR / "INSEE/2019/Évolution et structure de la population/BTX_TD_POP6_2019.xlsx",
}

PROCESSED_DATA_FILES = {
}
