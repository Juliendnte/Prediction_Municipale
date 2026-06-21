import pandas as pd
from .config import RAW_DATA_FILES, URLS
import re

def _read_insee_excel_sheet(filepath, sheet_name):
    return pd.read_excel(filepath, sheet_name=sheet_name, dtype=str)


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
    tour_courant = None

    with open(RAW_DATA_FILES['2008_res'], encoding='iso-8859-1') as f:
        lignes = [l.rstrip('\n').rstrip(';') for l in f if l.strip()]

    for line in lignes:
        # Détection des marqueurs de tour
        stripped = line.strip()
        if stripped == 'Tour1':
            tour_courant = 1
            continue
        elif stripped == 'Tour2':
            tour_courant = 2
            continue

        champs = line.split(';')
        if len(champs) < N_FIXES:
            continue

        fixes = champs[:N_FIXES]
        # Ignorer la ligne d'en-tête
        if fixes[0].startswith('Date'):
            continue

        reste = champs[N_FIXES:]
        n_listes = len(reste) // N_LISTE

        for i in range(n_listes):
            bloc_liste = reste[i * N_LISTE:(i + 1) * N_LISTE]
            if len(bloc_liste) < N_LISTE:
                continue
            blocs.append(fixes + bloc_liste + [tour_courant])

    df = pd.DataFrame(blocs, columns=COLS_FIXES + COLS_LISTE + ['Tour'])

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

def _load_and_clean_2026_res(tour):
    filepath = RAW_DATA_FILES['2026_res_tour' + str(tour)]
    COLS_FIXES = [
        'Code département', 'Libellé département',
        'Code commune', 'Libellé commune', 'Code BV',
        'Inscrits', 'Votants', '% Votants',
        'Abstentions', '% Abstentions',
        'Exprimés', '% Exprimés/inscrits', '% Exprimés/votants',
        'Blancs', '% Blancs/inscrits', '% Blancs/votants',
        'Nuls', '% Nuls/inscrits', '% Nuls/votants',
    ]
    COLS_LISTE = [
        'N° panneau', 'Nom', 'Prénom', 'Sexe',
        'Code Nuance', 'Libellé abrégé liste', 'Libellé liste',
        'Voix', '% Voix/inscrits', '% Voix/exprimés',
        'Elu', 'Sièges CM', 'Sièges CC',
    ]
    N_FIXES = len(COLS_FIXES)
    N_LISTE = len(COLS_LISTE)

    df_raw = pd.read_csv(filepath, sep=';', encoding='utf-8', header=0, dtype=str)

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
            if len(bloc_liste) < N_LISTE:
                continue
            # Ignorer les blocs vides (pas de numéro de panneau)
            if pd.isna(bloc_liste[0]) or str(bloc_liste[0]).strip() == '':
                continue
            blocs.append(fixes + bloc_liste + [tour])

    df = pd.DataFrame(blocs, columns=COLS_FIXES + COLS_LISTE + ['Tour'])

    cols_numeriques = ['Inscrits', 'Votants', 'Abstentions', 'Exprimés', 'Blancs', 'Nuls', 'Voix']
    for col in cols_numeriques:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    cols_pct = [
        '% Votants', '% Abstentions', '% Exprimés/inscrits', '% Exprimés/votants',
        '% Blancs/inscrits', '% Blancs/votants', '% Nuls/inscrits', '% Nuls/votants',
        '% Voix/inscrits', '% Voix/exprimés',
    ]
    for col in cols_pct:
        df[col] = pd.to_numeric(df[col].str.replace(',', '.').str.replace('%', '').str.strip(), errors='coerce')

    df = df.dropna(subset=['Voix'])

    return df

def _extract_insee_variable_metadata(filepath):
    """
    Lit la feuille 'Liste des variables' d'un fichier INSEE et extrait les libellés
    des modalités, par exemple :
    SEXE -> 1 Hommes, 2 Femmes
    AGEQ65 -> 015 15 à 19 ans
    DIPL_15 -> A Aucun diplôme...
    """
    df_meta = pd.read_excel(filepath, sheet_name="Liste des variables", header=None, dtype=str)
    lines = (
        df_meta.fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
        .str.strip()
        .tolist()
    )

    metadata = {}
    current_variable = None

    variable_pattern = re.compile(r"^([A-Z0-9_]+)\s*:\s*(.+)$")
    modality_pattern = re.compile(r"^([A-Z0-9]+)\s*:\s*(.+)$")

    for line in lines:
        if not line:
            continue

        variable_match = variable_pattern.match(line)
        if variable_match:
            current_variable = variable_match.group(1)
            metadata[current_variable] = {}
            continue

        modality_match = modality_pattern.match(line)
        if current_variable and modality_match:
            code = modality_match.group(1)
            label = modality_match.group(2)
            metadata[current_variable][code] = label

    return metadata


def _read_excel_data(path, sheet_name, header_row=None, nrows=None, skip_rows=None):
    df = pd.read_excel(
        path,
        sheet_name=sheet_name,
        header=header_row,
        nrows=nrows,
        skiprows=skip_rows,
    )
    df.columns = df.columns.astype(str).str.strip()
    return df

def _build_mapping_from_single_column_df(df, separator=":"):
    if df.shape[1] != 1:
        raise ValueError("Le DataFrame doit contenir une seule colonne.")
    mapping = {}
    for value in df.iloc[:, 0].dropna():
        value = str(value).strip()
        if separator not in value:
            continue
        code, label = value.split(separator, 1)
        key = code.strip()
        mapping[key] = label.strip()
    return mapping

def _load_and_group_insee_data(file_path: str, sheet_name: str, variables_mapping: dict[str, dict[str, str]], separated_columns: list[str] = []) -> pd.DataFrame:
    df = _read_excel_data(
        file_path,
        sheet_name=sheet_name,
        header_row=8
    )

    # Round and convert to numeric, replacing non-numeric values with NaN
    df = df.round(0).apply(pd.to_numeric, errors='coerce')
    # Convert to int, ignoring errors for non-numeric columns  
    for col in df.columns:
        df[col] = df[col].astype('int', errors='ignore')  

    columns = list(df.columns)
    # Remove separated columns from the list of columns to process
    for col in separated_columns:
        if col in columns:
            columns.remove(col)

    flattened_data = []
    variables = list(variables_mapping.keys())

    for index, row in df.iterrows():
        # Retrieve separated columns and add them to the row dictionary
        separated_values = {}
        for col in separated_columns:
            separated_values[col] = row[col]
        
        for col in columns:
            value = int(row[col])

            col_simplified = col
            for var in variables:
                col_simplified = col_simplified.replace(var, '').strip()

            split_parts = col_simplified.split('_')
            if len(split_parts) != len(variables):
                raise ValueError(f"Le nom de la colonne '{col}' ne correspond pas au format attendu.")
    
            row_to_add = {
                **separated_values
            }
            
            for i, var in enumerate(variables):
                code = split_parts[i]
                label = variables_mapping[var].get(code, None)
                row_to_add[var] = label
            
            row_to_add["Nombre"] = value

            flattened_data.append(row_to_add)

    df_flattened = pd.DataFrame(flattened_data)

    return df_flattened

def load_and_clean_insee_2007_famille(sheet: str = "COM") -> pd.DataFrame:
    """
    Charge les données de la feuille "COM" du fichier BTX_TD_FAM4_2007.xls

    Args:
        sheet (str): Nom de la feuille à charger. Par défaut "COM".
    """
    file_path = RAW_DATA_FILES['INSEE_2007_Fam']

    df_cs2_24 = _read_excel_data(
        file_path,
        sheet_name="liste_variables",
        header_row=7,
        nrows=24
    )

    df_nbenffr = _read_excel_data(
        file_path,
        sheet_name="liste_variables",
        header_row=32,
        nrows=5
    )
    cs2_24_mapping = _build_mapping_from_single_column_df(df_cs2_24)
    nbenffr_mapping = _build_mapping_from_single_column_df(df_nbenffr)

    df = _load_and_group_insee_data(
        file_path=file_path,
        sheet_name=sheet,
        separated_columns=["CODGEO"],
        variables_mapping={
            "CS2_24": cs2_24_mapping,
            "NBENFFR": nbenffr_mapping
        }
    )
    return df