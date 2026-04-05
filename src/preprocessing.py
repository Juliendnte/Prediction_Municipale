import pandas as pd
from .config import RAW_DATA_FILES, URLS


def load_and_clean_candidats():
 df = pd.read_excel(RAW_DATA_FILES['livre-des-listes-et-candidats'], skiprows=2)
 return df

def load_and_clean_candidats_stats():
 df = pd.read_csv(RAW_DATA_FILES['candidats_stat'], sep=';')
 return df

def load_and_clean_nuances():
 df = pd.read_csv(RAW_DATA_FILES['nuances'])
 return df

def load_and_clean_ville_stats():
 df = pd.read_csv(URLS['ville_stat'], sep=';', low_memory=False, on_bad_lines='skip')
 return df

def load_and_clean_ville_stats_histo():
 df1 = pd.read_csv(RAW_DATA_FILES['stat_ville_histo'], sep=';')
 df2 = pd.read_csv(RAW_DATA_FILES['stat_ville_histo_metadata'], sep=';')
 return df1, df2

def load_and_clean_2020_res_tour1():
 df = pd.read_excel(RAW_DATA_FILES['2020_res_tour1'])
 return df

def load_and_clean_2020_res_tour2():
 df = pd.read_excel(RAW_DATA_FILES['2020_res_tour2'])
 return df

def load_and_clean_2001_res():
 df = pd.read_excel(RAW_DATA_FILES['2001_res'])
 return df

def load_and_clean_2008_res():
 df = pd.read_csv(RAW_DATA_FILES['2008_res'], sep=';' , encoding='iso-8859-1')
 return df

def load_and_clean_2014_res():
 df = pd.read_csv(RAW_DATA_FILES['2014_res'], sep=';', encoding='iso-8859-1')
 return df


