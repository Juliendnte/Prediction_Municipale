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

# ... existing code ...

def load_and_clean_2020_res_tour1():
    return _load_and_clean_2020_res(RAW_DATA_FILES['2020_res_tour1'])

def load_and_clean_2020_res_tour2():
    return _load_and_clean_2020_res(RAW_DATA_FILES['2020_res_tour2'])

def _load_and_clean_2020_res(filepath):
    COLS_FIXES = [
        'Code du département', 'Libellé du département',
        'Code de la commune', 'Libellé de la commune', 'Code du bureau de vote',
        'Inscrits', 'Abstentions', '% Abs/Ins',
        'Votants', '% Vot/Ins',
        'Blancs', '% Blancs/Ins', '% Blancs/Vot',
        'Nuls', '% Nuls/Ins', '% Nuls/Vot',
        'Exprimés', '% Exp/Ins', '% Exp/Vot'
    ]
    COLS_LISTE = ['N.Pan.', 'Code Nuance', 'Sexe', 'Nom', 'Prénom', 'Liste', 'Voix', '% Voix/Ins', '% Voix/Exp']
    N_FIXES = len(COLS_FIXES)
    N_LISTE = len(COLS_LISTE)

    df_raw = pd.read_excel(filepath, header=0)

    blocs = []
    for _, row in df_raw.iterrows():
        vals = list(row)
        if len(vals) < N_FIXES:
            continue

        fixes = vals[:N_FIXES]
        reste = vals[N_FIXES:]
        n_listes = len(reste) // N_LISTE

        for i in range(n_listes):
            bloc_liste = reste[i * N_LISTE:(i + 1) * N_LISTE]
            # Ignorer les blocs vides (toutes les valeurs sont NaN)
            if pd.isna(bloc_liste[1]):  # Code Nuance vide = pas de liste
                continue
            blocs.append(fixes + bloc_liste)

    df = pd.DataFrame(blocs, columns=COLS_FIXES + COLS_LISTE)

    cols_numeriques = ['Inscrits', 'Abstentions', 'Votants', 'Blancs', 'Nuls', 'Exprimés', 'Voix']
    for col in cols_numeriques:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    cols_pct = ['% Abs/Ins', '% Vot/Ins', '% Blancs/Ins', '% Blancs/Vot',
                '% Nuls/Ins', '% Nuls/Vot', '% Exp/Ins', '% Exp/Vot',
                '% Voix/Ins', '% Voix/Exp']
    for col in cols_pct:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna(subset=['Voix'])

    return df

def load_and_clean_2001_res():
 COLS_FIXES = [
  'Code du département', 'Libellé du département',
  'Code de la commune', 'Libellé de la commune',
  'Population', 'Inscrits',
  'Abstentions', '% Abs/Ins',
  'Votants', '% Vot/Ins',
  'Blancs et nuls', '% BlNuls/Ins', '% BlNuls/Vot',
  'Exprimés', '% Exp/Ins', '% Exp/Vot'
 ]

 # Colonnes répétées par liste (groupe de 5 colonnes)
 COLS_LISTE = ['Nuance Liste', 'Libellé Abrégé Liste', 'Voix', '% Voix/Ins', '% Voix/Exp']
 df_raw = pd.read_excel(RAW_DATA_FILES['2001_res'])
 # --- Partie fixe ---
 df_fixed = df_raw.iloc[:, :16].copy()
 df_fixed.columns = COLS_FIXES

 # --- Partie listes : regrouper par blocs de 5 colonnes ---
 liste_cols = df_raw.iloc[:, 16:]
 n_listes = len(liste_cols.columns) // 5

 blocs = []
 for i in range(n_listes):
  bloc = liste_cols.iloc[:, i * 5: i * 5 + 5].copy()
  bloc.columns = COLS_LISTE
  # Ajouter un numéro de rang de liste (optionnel)
  bloc['rang_liste'] = i + 1
  # Réattacher les colonnes fixes
  bloc = pd.concat([df_fixed.reset_index(drop=True), bloc.reset_index(drop=True)], axis=1)
  blocs.append(bloc)

 df_long = pd.concat(blocs, ignore_index=True)

 # Supprimer les lignes sans liste (cases vides pour communes avec peu de listes)
 df_long = df_long.dropna(subset=['Nuance Liste', 'Voix'])

 return df_long
 return df

def load_and_clean_2008_res():
    COLS_FIXES = [
        'Date export', 'Code du département', 'Libellé du département',
        'Code de la commune', 'Libellé de la commune', 'Code du bureau de vote',
        'Inscrits', 'Abstentions', '% Abs/Ins',
        'Votants', '% Vot/Ins',
        'Blancs et nuls', '% BlNuls/Ins', '% BlNuls/Vot',
        'Exprimés', '% Exp/Ins', '% Exp/Vot'
    ]
    COLS_LISTE = ['Code Nuance', 'Sexe', 'Nom', 'Prénom', 'Liste', 'Sièges', 'Voix', '% Voix/Ins', '% Voix/Exp']
    N_FIXES = len(COLS_FIXES)
    N_LISTE = len(COLS_LISTE)

    blocs = []
    with open(RAW_DATA_FILES['2008_res'], encoding='iso-8859-1') as f:
        lignes = [l.rstrip('\n').rstrip(';') for l in f if l.strip()]

    # La première ligne non-vide est l'en-tête, on la saute
    for line in lignes[1:]:
        champs = line.split(';')
        if len(champs) < N_FIXES:
            continue

        fixes = champs[:N_FIXES]
        # Vérification : le 1er champ fixes doit ressembler à une date, pas à un nom de colonne
        if fixes[0].startswith('Date'):
            continue

        reste = champs[N_FIXES:]
        n_listes = len(reste) // N_LISTE

        for i in range(n_listes):
            bloc_liste = reste[i * N_LISTE:(i + 1) * N_LISTE]
            if len(bloc_liste) < N_LISTE:
                continue
            blocs.append(fixes + bloc_liste)

    df = pd.DataFrame(blocs, columns=COLS_FIXES + COLS_LISTE)

    # Nettoyage des types numériques entiers
    cols_numeriques = ['Inscrits', 'Abstentions', 'Votants', 'Blancs et nuls', 'Exprimés', 'Sièges', 'Voix']
    for col in cols_numeriques:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Nettoyage des pourcentages (virgule → point)
    cols_pct = ['% Abs/Ins', '% Vot/Ins', '% BlNuls/Ins', '% BlNuls/Vot',
                '% Exp/Ins', '% Exp/Vot', '% Voix/Ins', '% Voix/Exp']
    for col in cols_pct:
        df[col] = pd.to_numeric(df[col].str.replace(',', '.'), errors='coerce')

    df = df.dropna(subset=['Voix'])

    return df


def load_and_clean_2014_res():
 df = pd.read_csv(RAW_DATA_FILES['2014_res'], sep=';', encoding='iso-8859-1', low_memory=False)
 return df


