import pandas as pd
from .config import RAW_DATA_FILES, PROCESSED_DATA_FILES
import re

def _read_insee_excel_sheet(filepath, sheet_name):
    return pd.read_excel(filepath, sheet_name=sheet_name, dtype=str)


def load_and_clean_nuances():
 df = pd.read_csv(RAW_DATA_FILES['nuances'])
 return df

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
            if tour_courant is None:
                continue  # ignorer les lignes avant le premier marqueur de tour
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

def load_and_clean_processed_res():
    df = pd.read_csv(PROCESSED_DATA_FILES['res_all'], sep=';', encoding='utf-8', low_memory=False)
    return df


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
    for h in [8, 9, 10]:

        df = _read_excel_data(
            file_path,
            sheet_name=sheet_name,
            header_row=h,
        )
        if "CODGEO" in df.columns:
            break

    # Round and convert to numeric, replacing non-numeric values with NaN
    df = df.round(0).apply(pd.to_numeric, errors='coerce')
    # Convert to int, ignoring errors for non-numeric columns
    # Convert to int, ignoring errors for non-numeric columns
    for col in df.columns:
        df[col] = df[col].astype('int', errors='ignore')
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

def load_and_clean_insee_2007_menage(sheet: str = "COM") -> pd.DataFrame:
    """
    Charge les données de la feuille "COM" du fichier BTX_TD_MEN1_2007.xls

    Args:
        sheet (str): Nom de la feuille à charger. Par défaut "COM".
    """
    file_path = RAW_DATA_FILES['INSEE_2007_Men']

    df_cs2_24 = _read_excel_data(
        file_path,
        sheet_name="liste_variables",
        header_row=7,
        nrows=24
    )

    df_nperc = _read_excel_data(
        file_path,
        sheet_name="liste_variables",
        header_row=32,
        nrows=6
    )
    cs2_24_mapping = _build_mapping_from_single_column_df(df_cs2_24)
    nperc_mapping = _build_mapping_from_single_column_df(df_nperc)

    df = _load_and_group_insee_data(
        file_path=file_path,
        sheet_name=sheet,
        separated_columns=["CODGEO"],
        variables_mapping={
            "CS2_24": cs2_24_mapping,
            "NPERC": nperc_mapping
        }
    )

    return df

def load_and_clean_insee_2007_diplome(sheet: str = "COM") -> pd.DataFrame:
    """
    Charge les données de la feuille "COM" du fichier BTX_TD_FOR2_2007.xls

    Args:
        sheet (str): Nom de la feuille à charger. Par défaut "COM".
    """
    file_path = RAW_DATA_FILES['INSEE_2007_Dip']

    df_sexe = _read_excel_data(
        file_path,
        sheet_name="Liste des variables",
        header_row=7,
        nrows=2
    )

    df_ageq65 = _read_excel_data(
        file_path,
        sheet_name="Liste des variables",
        header_row=10,
        nrows=11
    )

    df_dipl = _read_excel_data(
        file_path,
        sheet_name="Liste des variables",
        header_row=22,
        nrows=11
    )

    sexe_mapping = _build_mapping_from_single_column_df(df_sexe)
    ageq65_mapping = _build_mapping_from_single_column_df(df_ageq65)
    dipl_mapping = _build_mapping_from_single_column_df(df_dipl)

    #print("sexe", sexe_mapping, "ageq65", ageq65_mapping, "dipl", dipl_mapping)

    df = _load_and_group_insee_data(
        file_path=file_path,
        sheet_name=sheet,
        separated_columns=["CODGEO"],
        variables_mapping={
            "SEXE": sexe_mapping,
            "AGEQ65": ageq65_mapping,
            "DIPL": dipl_mapping
        }
    )

    return df

def load_and_clean_insee_2007_population(sheet: str = "COM") -> pd.DataFrame:
    """
    Charge les données de la feuille "COM" du fichier BTX_TD_POP5_2007.xls

    Args:
        sheet (str): Nom de la feuille à charger. Par défaut "COM".
    """
    file_path = RAW_DATA_FILES['INSEE_2007_Pop']

    df_sexe = _read_excel_data(
        file_path,
        sheet_name="liste_variables",
        header_row=7,
        nrows=2
    )

    df_ageq65 = _read_excel_data(
        file_path,
        sheet_name="liste_variables",
        header_row=10,
        nrows=11
    )

    df_tactr = _read_excel_data(
        file_path,
        sheet_name="liste_variables",
        header_row=22,
        nrows=11
    )

    sexe_mapping = _build_mapping_from_single_column_df(df_sexe)
    ageq65_mapping = _build_mapping_from_single_column_df(df_ageq65)
    tactr_mapping = _build_mapping_from_single_column_df(df_tactr)

    #print("sexe", sexe_mapping, "ageq65", ageq65_mapping, "tactr", tactr_mapping)

    df = _load_and_group_insee_data(
        file_path=file_path,
        sheet_name=sheet,
        separated_columns=["CODGEO"],
        variables_mapping={
            "SEXE": sexe_mapping,
            "AGEQ65": ageq65_mapping,
            "TACTR": tactr_mapping
        }
    )

    return df

def load_and_clean_insee_2007_population2(sheet: str = "COM") -> pd.DataFrame:
    """
    Charge les données de la feuille "COM" du fichier BTX_TD_POP6_2007.xls

    Args:
        sheet (str): Nom de la feuille à charger. Par défaut "COM".
    """
    file_path = RAW_DATA_FILES['INSEE_2007_Pop']

    df_sexe = _read_excel_data(
        file_path,
        sheet_name="liste_variables",
        header_row=7,
        nrows=2
    )

    df_ageq65 = _read_excel_data(
        file_path,
        sheet_name="liste_variables",
        header_row=10,
        nrows=11
    )

    df_cs1_8 = _read_excel_data(
        file_path,
        sheet_name="liste_variables",
        header_row=22,
        nrows=8
    )

    sexe_mapping = _build_mapping_from_single_column_df(df_sexe)
    ageq65_mapping = _build_mapping_from_single_column_df(df_ageq65)
    cs1_8_mapping = _build_mapping_from_single_column_df(df_cs1_8)

    #print("sexe", sexe_mapping, "ageq65", ageq65_mapping, "tactr", tactr_mapping)

    df = _load_and_group_insee_data(
        file_path=file_path,
        sheet_name=sheet,
        separated_columns=["CODGEO"],
        variables_mapping={
            "SEXE": sexe_mapping,
            "AGEQ65": ageq65_mapping,
            "CS1_8": cs1_8_mapping
        }
    )

    return df

def load_and_clean_insee_2007_immigration(sheet: str = "COM") -> pd.DataFrame:
    """
    Charge les données de la feuille "COM" du fichier BTX_TD_IMG1_2007.xls

    Args:
        sheet (str): Nom de la feuille à charger. Par défaut "COM".
    """
    file_path = RAW_DATA_FILES['INSEE_2007_Img']

    df_sexe = _read_excel_data(
        file_path,
        sheet_name="Liste_variables",
        header_row=8,
        nrows=2
    )

    df_age4 = _read_excel_data(
        file_path,
        sheet_name="Liste_variables",
        header_row=11,
        nrows=4
    )

    df_tactr = _read_excel_data(
        file_path,
        sheet_name="Liste_variables",
        header_row=16,
        nrows=6
    )

    df_immi = _read_excel_data(
        file_path,
        sheet_name="Liste_variables",
        header_row=23,
        nrows=2
    )

    sexe_mapping = _build_mapping_from_single_column_df(df_sexe)
    age4_mapping = _build_mapping_from_single_column_df(df_age4)
    tactr_mapping = _build_mapping_from_single_column_df(df_tactr)
    immi_mapping = _build_mapping_from_single_column_df(df_immi)


    #print("sexe", sexe_mapping, "ageq65", ageq65_mapping, "tactr", tactr_mapping)

    df = _load_and_group_insee_data(
        file_path=file_path,
        sheet_name=sheet,
        separated_columns=["CODGEO"],
        variables_mapping={
            "SEXE": sexe_mapping,
            "AGE4": age4_mapping,
            "TACTR": tactr_mapping,
            "IMMI": immi_mapping
        }
    )

    return df

def load_and_clean_insee_2007_nationalite(sheet: str = "COM") -> pd.DataFrame:
    """
    Charge les données de la feuille "COM" du fichier BTX_TD_NAT1_2007.xls

    Args:
        sheet (str): Nom de la feuille à charger. Par défaut "COM".
    """
    file_path = RAW_DATA_FILES['INSEE_2007_Nat']

    df_sexe = _read_excel_data(
        file_path,
        sheet_name="Liste des variables",
        header_row=6,
        nrows=2
    )

    df_inatc = _read_excel_data(
        file_path,
        sheet_name="Liste des variables",
        header_row=9,
        nrows=2
    )

    df_age4 = _read_excel_data(
        file_path,
        sheet_name="Liste des variables",
        header_row=12,
        nrows=4
    )


    sexe_mapping = _build_mapping_from_single_column_df(df_sexe)
    inatc_mapping = _build_mapping_from_single_column_df(df_inatc)
    age4_mapping = _build_mapping_from_single_column_df(df_age4)


    #print("sexe", sexe_mapping, "ageq65", ageq65_mapping, "tactr", tactr_mapping)

    df = _load_and_group_insee_data(
        file_path=file_path,
        sheet_name=sheet,
        separated_columns=["CODGEO"],
        variables_mapping={
            "SEXE": sexe_mapping,
            "INATC": inatc_mapping,
            "AGE4": age4_mapping,
        }
    )

    return df

def load_and_clean_insee_2007_nationalite2(sheet: str = "COM") -> pd.DataFrame:
    """
    Charge les données de la feuille "COM" du fichier BTX_TD_NAT3_2007.xls

    Args:
        sheet (str): Nom de la feuille à charger. Par défaut "COM".
    """
    file_path = RAW_DATA_FILES['INSEE_2007_Nat2']

    df_sexe = _read_excel_data(
        file_path,
        sheet_name="Liste des variables",
        header_row=7,
        nrows=2
    )

    df_inatc = _read_excel_data(
        file_path,
        sheet_name="Liste des variables",
        header_row=10,
        nrows=2
    )

    df_cs1_8 = _read_excel_data(
        file_path,
        sheet_name="Liste des variables",
        header_row=13,
        nrows=8
    )


    sexe_mapping = _build_mapping_from_single_column_df(df_sexe)
    inatc_mapping = _build_mapping_from_single_column_df(df_inatc)
    cs1_8_mapping = _build_mapping_from_single_column_df(df_cs1_8)


    #print("sexe", sexe_mapping, "ageq65", ageq65_mapping, "tactr", tactr_mapping)

    df = _load_and_group_insee_data(
        file_path=file_path,
        sheet_name=sheet,
        separated_columns=["CODGEO"],
        variables_mapping={
            "SEXE": sexe_mapping,
            "INATC": inatc_mapping,
            "CS1_8": cs1_8_mapping,
        }
    )

    return df

def load_and_clean_insee_2007_logement(sheet: str = "COM") -> pd.DataFrame:
    """
    Charge les données de la feuille "COM" du fichier BTX_TD_PRINC14_2007.xls

    Args:
        sheet (str): Nom de la feuille à charger. Par défaut "COM".
    """
    file_path = RAW_DATA_FILES['INSEE_2007_Log']

    df_typlr = _read_excel_data(
        file_path,
        sheet_name="Liste des variables",
        header_row=6,
        nrows=3
    )

    df_cs1_8 = _read_excel_data(
        file_path,
        sheet_name="Liste des variables",
        header_row=10,
        nrows=8
    )

    df_stocd = _read_excel_data(
        file_path,
        sheet_name="Liste des variables",
        header_row=19,
        nrows=5
    )

    typlr_mapping = _build_mapping_from_single_column_df(df_typlr)
    cs1_8_mapping = _build_mapping_from_single_column_df(df_cs1_8)
    stocd_mapping = _build_mapping_from_single_column_df(df_stocd)

    #print("sexe", sexe_mapping, "ageq65", ageq65_mapping, "tactr", tactr_mapping)

    df = _load_and_group_insee_data(
        file_path=file_path,
        sheet_name=sheet,
        separated_columns=["CODGEO"],
        variables_mapping={
            "TYPLR": typlr_mapping,
            "CS1_8": cs1_8_mapping,
            "STOCD": stocd_mapping,
        }
    )

    return df

def load_and_clean_insee_2007_emploi(sheet: str = "COM") -> pd.DataFrame:
    """
    Charge les données de la feuille "COM" du fichier BTX_TD_EMP3_2007.xls

    Args:
        sheet (str): Nom de la feuille à charger. Par défaut "COM".
    """
    file_path = RAW_DATA_FILES['INSEE_2007_Emp']

    df_sexe = _read_excel_data(
        file_path,
        sheet_name="liste_variables",
        header_row=6,
        nrows=2
    )

    df_cs3_31 = _read_excel_data(
        file_path,
        sheet_name="liste_variables",
        header_row=10,
        nrows=31
    )

    df_na5 = _read_excel_data(
        file_path,
        sheet_name="liste_variables",
        header_row=42,
        nrows=6
    )

    sexe_mapping = _build_mapping_from_single_column_df(df_sexe)
    cs3_31_mapping = _build_mapping_from_single_column_df(df_cs3_31)
    na5_mapping = _build_mapping_from_single_column_df(df_na5)

    #print("sexe", sexe_mapping, "ageq65", ageq65_mapping, "tactr", tactr_mapping)

    df = _load_and_group_insee_data(
        file_path=file_path,
        sheet_name=sheet,
        separated_columns=["CODGEO"],
        variables_mapping={
            "SEXE": sexe_mapping,
            "CS3_31": cs3_31_mapping,
            "NA5": na5_mapping,
        }
    )

    return df





def load_and_clean_processed_analysis_municipal():
    df = pd.read_csv(PROCESSED_DATA_FILES['analysis_municipal'], sep=';', encoding='utf-8', low_memory=False)
    return df

# ============================================================================
# == INSEE 2013 & 2019 — moteur de chargement auto-descriptif ================
# ============================================================================
# Pourquoi un nouveau moteur plutôt que réutiliser les fonctions 2007 ?
# Les fichiers 2013/2019 ont la MÊME logique que 2007 mais :
#   - les numéros de ligne (header_row/nrows) codés en dur ne tombent plus juste ;
#   - le nom d'une variable change selon l'année (DIPL -> DIPL_15 -> DIPL_19,
#     AGE4 -> AGE_4, CS3_31 -> CS3_29) ;
#   - l'INSEE écrit parfois le même code avec ou sans préfixe ('00' vs 'AGE400'),
#     et nomme la variable différemment entre l'en-tête de données et la feuille
#     'Liste des variables' (AGE_4 vs AGE4).
# Ces fichiers étant AUTO-DESCRIPTIFS (un bloc 'Variables :' liste les variables
# croisées juste au-dessus de la ligne CODGEO), on lit la structure directement
# dans le fichier au lieu de la coder en dur. Compatible .xls (xlrd) et .xlsx.

def _insee_norm(s: str) -> str:
    # retire espaces/underscores, garde les points : 'C.O.M.' != 'COM'
    return re.sub(r"[\s_]", "", str(s).lower())


def _insee_find_sheet(path, *candidates) -> str:
    xls = pd.ExcelFile(path)
    raw = {str(s).strip().lower(): s for s in xls.sheet_names}
    available = {_insee_norm(s): s for s in xls.sheet_names}
    for c in candidates:                       # 1) brute exacte (casse ignorée)
        if str(c).strip().lower() in raw:
            return raw[str(c).strip().lower()]
    for c in candidates:                       # 2) normalisée exacte
        if _insee_norm(c) in available:
            return available[_insee_norm(c)]
    for c in candidates:                       # 3) inclusion (points bloquants)
        nc = _insee_norm(c)
        for k, real in available.items():
            if nc and (nc in k or k in nc):
                return real
    raise ValueError(
        f"Aucune feuille parmi {candidates} dans {path}. "
        f"Feuilles disponibles : {xls.sheet_names}"
    )


def _insee_detect_structure(path, sheet, max_scan: int = 25):
    """Renvoie (feuille, header_row, [variables], [lignes_variables], top_df)."""
    real_sheet = _insee_find_sheet(path, sheet)
    top = pd.read_excel(
        path, sheet_name=real_sheet, header=None, nrows=max_scan, dtype=str
    ).fillna("")

    header_row = None
    for i in range(len(top)):
        if str(top.iat[i, 0]).strip().upper() == "CODGEO":
            header_row = i
            break
    if header_row is None:
        raise ValueError(f"'CODGEO' introuvable dans '{real_sheet}' ({path}).")

    var_start = None
    for i in range(header_row):
        if str(top.iat[i, 0]).strip().lower().startswith("variables"):
            var_start = i
            break
    if var_start is None:
        raise ValueError(f"Bloc 'Variables :' introuvable dans '{real_sheet}' ({path}).")

    col_var = 1 if top.shape[1] > 1 else 0
    variables, var_rows = [], []
    for i in range(var_start, header_row):
        name = str(top.iat[i, col_var]).strip()
        if name:
            variables.append(name)
            var_rows.append(i)
        elif variables:
            break
    if not variables:
        raise ValueError(f"Aucune variable lue dans '{real_sheet}' ({path}).")
    return real_sheet, header_row, variables, var_rows, top


def _insee_extract_modalities(path, variables, variables_sheet=None):
    """Renvoie {VARIABLE: {code: libellé}} (appariement tolérant aux underscores)."""
    if variables_sheet is None:
        variables_sheet = _insee_find_sheet(
            path, "Liste des variables", "liste_variables", "Liste_variables",
            "Liste variables", "Variables",
        )
    raw = pd.read_excel(path, sheet_name=variables_sheet, header=None, dtype=str)
    lines = (
        raw.fillna("").astype(str).agg(" ".join, axis=1)
        .str.replace(r"\s+", " ", regex=True).str.strip().tolist()
    )

    def _vnorm(s):
        return re.sub(r"[^A-Z0-9]", "", str(s).upper())

    norm_to_var = {_vnorm(v): v for v in variables}
    metadata = {v: {} for v in variables}
    current = None
    for line in lines:
        if not line or ":" not in line:
            continue
        left, right = line.split(":", 1)
        code, label = left.strip(), right.strip()
        if not code or not label:
            continue
        if _vnorm(code) in norm_to_var:
            current = norm_to_var[_vnorm(code)]
        elif current is not None:
            metadata[current][code] = label

    missing = [v for v in variables if not metadata[v]]
    if missing:
        raise ValueError(
            f"Aucune modalité trouvée pour {missing} dans '{variables_sheet}' ({path})."
        )
    return metadata


def _insee_resolve_code(cell, codes_by_len):
    """Retrouve le code (cellule = code, ou se termine par le code connu le plus long)."""
    cell = str(cell).strip()
    for c in codes_by_len:
        if cell == c or cell.endswith(c):
            return c
    return None


_INSEE_ID_COLS = ["CODGEO", "LIBGEO"]


def load_insee_file(path, sheet: str = "COM", as_int: bool = True,
                    rename: dict | None = None) -> pd.DataFrame:
    """Charge une table INSEE BTX_TD (2007/2013/2019) en format long.

    Colonnes de sortie : CODGEO, LIBGEO, <une colonne par variable>, Nombre.

    Args:
        path: chemin .xls / .xlsx.
        sheet: feuille de données ('COM' par défaut, tolérante à la casse).
        as_int: arrondit les effectifs à l'entier (comme les loaders 2007).
        rename: renommage des colonnes de variables, ex. {'DIPL_15': 'DIPL'}.
    """
    real_sheet, header_row, variables, var_rows, top = _insee_detect_structure(path, sheet)
    mapping = _insee_extract_modalities(path, variables)
    codes_by_len = {v: sorted(mapping[v].keys(), key=len, reverse=True) for v in variables}

    df = pd.read_excel(path, sheet_name=real_sheet, header=header_row, dtype=str)
    df.columns = df.columns.astype(str).str.strip()
    sep_cols = [c for c in _INSEE_ID_COLS if c in df.columns]

    frames = []
    for m, col in enumerate(df.columns):
        if col in sep_cols:
            continue
        if m >= top.shape[1]:
            raise ValueError(f"Désalignement bloc/données sur la colonne '{col}'.")
        labels = {}
        for var, vr in zip(variables, var_rows):
            code = _insee_resolve_code(top.iat[vr, m], codes_by_len[var])
            labels[var] = mapping[var].get(code)
        sub = pd.DataFrame({c: df[c] for c in sep_cols})
        for var in variables:
            sub[var] = labels[var]
        sub["Nombre"] = pd.to_numeric(df[col], errors="coerce")
        frames.append(sub)

    out = pd.concat(frames, ignore_index=True).dropna(subset=["Nombre"])
    if as_int:
        out["Nombre"] = out["Nombre"].round().astype(int)
    if rename:
        out = out.rename(columns=rename)
    return out.reset_index(drop=True)


# --- Renommages canoniques (différences de nom seules, même concept) ---------
# DIPL_15/DIPL_19 -> DIPL et AGE_4 -> AGE4, pour rester empilable avec 2007.
# NB : CS3_29 (2013/2019) n'est PAS renommé en CS3_31 (2007) car la nomenclature
# CSP a changé (29 vs 31 postes) ; de même les modalités du diplôme diffèrent
# d'une année à l'autre — seul le nom de colonne est harmonisé.
_RENAME_2013 = {"DIPL_15": "DIPL", "AGE_4": "AGE4"}
_RENAME_2019 = {"DIPL_19": "DIPL", "AGE_4": "AGE4"}


# ---------------------------------------------------------------------------
# Wrappers 2013 (mêmes signatures que les fonctions 2007)
# ---------------------------------------------------------------------------
def load_and_clean_insee_2013_famille(sheet: str = "COM") -> pd.DataFrame:
    """BTX_TD_FAM4_2013.xls — variables CS2_24, NBENFFR."""
    return load_insee_file(RAW_DATA_FILES['INSEE_2013_Fam'], sheet, rename=_RENAME_2013)

def load_and_clean_insee_2013_menage(sheet: str = "COM") -> pd.DataFrame:
    """BTX_TD_MEN1_2013.xls — variables CS2_24, NPERC."""
    return load_insee_file(RAW_DATA_FILES['INSEE_2013_Men'], sheet, rename=_RENAME_2013)

def load_and_clean_insee_2013_diplome(sheet: str = "COM") -> pd.DataFrame:
    """BTX_TD_FOR2_2013.xls — SEXE, AGEQ65, DIPL (=DIPL_15)."""
    return load_insee_file(RAW_DATA_FILES['INSEE_2013_Dip'], sheet, rename=_RENAME_2013)

def load_and_clean_insee_2013_population(sheet: str = "COM") -> pd.DataFrame:
    """BTX_TD_POP5_2013.xls — SEXE, AGEQ65, TACTR."""
    return load_insee_file(RAW_DATA_FILES['INSEE_2013_Pop'], sheet, rename=_RENAME_2013)

def load_and_clean_insee_2013_population2(sheet: str = "COM") -> pd.DataFrame:
    """BTX_TD_POP6_2013.xls — SEXE, AGEQ65, CS1_8."""
    return load_insee_file(RAW_DATA_FILES['INSEE_2013_Pop2'], sheet, rename=_RENAME_2013)

def load_and_clean_insee_2013_nationalite(sheet: str = "COM") -> pd.DataFrame:
    """BTX_TD_NAT1_2013.xls — SEXE, INATC, AGE4 (=AGE_4)."""
    return load_insee_file(RAW_DATA_FILES['INSEE_2013_Nat'], sheet, rename=_RENAME_2013)

def load_and_clean_insee_2013_nationalite2(sheet: str = "COM") -> pd.DataFrame:
    """BTX_TD_NAT3A_2013.xls — SEXE, INATC, CS1_8."""
    return load_insee_file(RAW_DATA_FILES['INSEE_2013_Nat2'], sheet, rename=_RENAME_2013)

def load_and_clean_insee_2013_logement(sheet: str = "COM") -> pd.DataFrame:
    """BTX_TD_PRINC14_2013.xls — TYPLR, CS1_8, STOCD."""
    return load_insee_file(RAW_DATA_FILES['INSEE_2013_Log'], sheet, rename=_RENAME_2013)

def load_and_clean_insee_2013_emploi(sheet: str = "COM") -> pd.DataFrame:
    """BTX_TD_EMP3_2013.xls — SEXE, CS3_29, NA5 (nomenclature CSP 29 postes)."""
    return load_insee_file(RAW_DATA_FILES['INSEE_2013_Emp'], sheet, rename=_RENAME_2013)

def load_and_clean_insee_2013_immigration(sheet: str = "COM") -> pd.DataFrame:
    """BTX_TD_IMG2A_2013.xls — SEXE, AGE4_A, IMMI, TACTR (feuille COM disponible)."""
    return load_insee_file(RAW_DATA_FILES['INSEE_2013_Img'], sheet, rename=_RENAME_2013)


# ---------------------------------------------------------------------------
# Wrappers 2019 (fichiers .xlsx)
# ---------------------------------------------------------------------------
def load_and_clean_insee_2019_famille(sheet: str = "COM") -> pd.DataFrame:
    """BTX_TD_FAM4_2019.xlsx — variables CS2_24, NBENFFR."""
    return load_insee_file(RAW_DATA_FILES['INSEE_2019_Fam'], sheet, rename=_RENAME_2019)

def load_and_clean_insee_2019_menage(sheet: str = "COM") -> pd.DataFrame:
    """BTX_TD_MEN1_2019.xlsx — variables CS2_24, NPERC."""
    return load_insee_file(RAW_DATA_FILES['INSEE_2019_Men'], sheet, rename=_RENAME_2019)

def load_and_clean_insee_2019_diplome(sheet: str = "COM") -> pd.DataFrame:
    """BTX_TD_FOR2_2019.xlsx — SEXE, AGEQ65, DIPL (=DIPL_19)."""
    return load_insee_file(RAW_DATA_FILES['INSEE_2019_Dip'], sheet, rename=_RENAME_2019)

def load_and_clean_insee_2019_population(sheet: str = "COM") -> pd.DataFrame:
    """BTX_TD_POP5_2019.xlsx — SEXE, AGEQ65, TACTR."""
    return load_insee_file(RAW_DATA_FILES['INSEE_2019_Pop'], sheet, rename=_RENAME_2019)

def load_and_clean_insee_2019_population2(sheet: str = "COM") -> pd.DataFrame:
    """BTX_TD_POP6_2019.xlsx — SEXE, AGEQ65, CS1_8."""
    return load_insee_file(RAW_DATA_FILES['INSEE_2019_Pop2'], sheet, rename=_RENAME_2019)

def load_and_clean_insee_2019_nationalite(sheet: str = "COM") -> pd.DataFrame:
    """BTX_TD_NAT1_2019.xlsx — SEXE, INATC, AGE4 (=AGE_4)."""
    return load_insee_file(RAW_DATA_FILES['INSEE_2019_Nat'], sheet, rename=_RENAME_2019)

def load_and_clean_insee_2019_nationalite2(sheet: str = "COM") -> pd.DataFrame:
    """BTX_TD_NAT3A_2019.xlsx — SEXE, INATC, CS1_8."""
    return load_insee_file(RAW_DATA_FILES['INSEE_2019_Nat2'], sheet, rename=_RENAME_2019)

def load_and_clean_insee_2019_logement(sheet: str = "COM") -> pd.DataFrame:
    """BTX_TD_PRINC14_2019.xlsx — TYPLR, CS1_8, STOCD."""
    return load_insee_file(RAW_DATA_FILES['INSEE_2019_Log'], sheet, rename=_RENAME_2019)

def load_and_clean_insee_2019_emploi(sheet: str = "COM") -> pd.DataFrame:
    """BTX_TD_EMP3_2019.xlsx — SEXE, CS3_29, NA5 (nomenclature CSP 29 postes)."""
    return load_insee_file(RAW_DATA_FILES['INSEE_2019_Emp'], sheet, rename=_RENAME_2019)

def load_and_clean_insee_2019_immigration(sheet: str = "COM") -> pd.DataFrame:
    """BTX_TD_COM_IMG2A_2019.xlsx.

    ATTENTION : ce fichier ne contient PAS de feuille 'COM' (communes) ; sa seule
    feuille de données est 'C.O.M.' (Collectivités d'Outre-Mer). Au niveau communal
    il n'y a donc pas de données ici. Passe sheet='C.O.M.' pour lire l'outre-mer,
    ou récupère le fichier communal détaillé correspondant auprès de l'INSEE.
    """
    return load_insee_file(RAW_DATA_FILES['INSEE_2019_Img'], sheet, rename=_RENAME_2019)
