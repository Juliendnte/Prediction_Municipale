"""
Chargement générique des tableaux détaillés INSEE (BTX_TD_*) — millésimes
2007 (.xls), 2013 (.xls) et 2019 (.xlsx).

Principe : ces fichiers sont AUTO-DESCRIPTIFS. La feuille de données (COM, ARM…)
contient, juste au-dessus de la ligne d'en-tête `CODGEO`, un bloc « Variables : »
qui liste les variables croisées dans l'ordre, par ex. pour la table FOR2 :

    Variables :   AGEQ65   015  015  ...
                  DIPL_15  A    A    ...
                  SEXE     1    2    ...
    ...
    CODGEO  LIBGEO  AGEQ65015_DIPL_15A_SEXE1  AGEQ65015_DIPL_15A_SEXE2  ...

On lit donc les noms de variables DIRECTEMENT dans le fichier (au lieu de les
coder en dur). Cela règle le piège des suffixes d'année (DIPL en 2007,
DIPL_15 en 2013, DIPL_19 en 2019) et fonctionne pour toutes les tables sans
maintenance.

Compatibilité .xls / .xlsx : on n'utilise que pandas.read_excel (xlrd pour .xls,
openpyxl pour .xlsx — les deux sont déjà dans tes dépendances).
"""

import re
import pandas as pd

try:
    from .config import RAW_DATA_FILES        # usage normal dans le package src
except ImportError:                            # usage hors package (tests, script)
    RAW_DATA_FILES = {}


# --------------------------------------------------------------------------- #
# Helpers feuilles
# --------------------------------------------------------------------------- #

def _norm(s: str) -> str:
    # On retire uniquement espaces et underscores (casse ignorée). On GARDE les
    # points : 'C.O.M.' (Collectivités d'Outre-Mer) ne doit PAS être confondu
    # avec 'COM' (Communes).
    return re.sub(r"[\s_]", "", str(s).lower())


def _find_sheet(path, *candidates) -> str:
    """Trouve une feuille par correspondance tolérante (casse, espaces, '_')."""
    xls = pd.ExcelFile(path)
    raw = {str(s).strip().lower(): s for s in xls.sheet_names}
    available = {_norm(s): s for s in xls.sheet_names}
    # 1) correspondance brute exacte (insensible à la casse)
    for c in candidates:
        if str(c).strip().lower() in raw:
            return raw[str(c).strip().lower()]
    # 2) correspondance normalisée exacte (espaces/underscores ignorés)
    for c in candidates:
        if _norm(c) in available:
            return available[_norm(c)]
    # 3) correspondance par inclusion (les points restent bloquants)
    for c in candidates:
        nc = _norm(c)
        for k, real in available.items():
            if nc and (nc in k or k in nc):
                return real
    raise ValueError(
        f"Aucune feuille parmi {candidates} dans {path}. "
        f"Feuilles disponibles : {xls.sheet_names}"
    )


# --------------------------------------------------------------------------- #
# Lecture de la structure (en-tête + variables) directement dans le fichier
# --------------------------------------------------------------------------- #

def _detect_structure(path, sheet, max_scan: int = 25):
    """Renvoie (feuille, header_row, [variables], [lignes_des_variables], top_df).

    Compatible .xls et .xlsx (lecture pandas, nrows limité => rapide même sur
    une feuille de 35 000 communes).
    """
    real_sheet = _find_sheet(path, sheet)
    top = pd.read_excel(
        path, sheet_name=real_sheet, header=None, nrows=max_scan, dtype=str
    ).fillna("")

    # 1) ligne d'en-tête = première ligne dont la 1re cellule vaut 'CODGEO'
    header_row = None
    for i in range(len(top)):
        if str(top.iat[i, 0]).strip().upper() == "CODGEO":
            header_row = i
            break
    if header_row is None:
        raise ValueError(
            f"'CODGEO' introuvable dans les {max_scan} premières lignes de "
            f"'{real_sheet}' ({path})."
        )

    # 2) bloc des variables. Deux mises en page existent :
    #    - 2013/2019 : une ligne 'Variables :' puis les noms en 2e colonne ;
    #    - 2007       : une ligne par variable 'NOM ->' en 1re colonne.
    variables, var_rows = [], []

    var_start = None
    for i in range(header_row):
        if str(top.iat[i, 0]).strip().lower().startswith("variables"):
            var_start = i
            break

    if var_start is not None:                      # mise en page 2013/2019
        col_var = 1 if top.shape[1] > 1 else 0
        for i in range(var_start, header_row):
            name = str(top.iat[i, col_var]).strip()
            if name:
                variables.append(name)
                var_rows.append(i)
            elif variables:
                break
    else:                                          # mise en page 2007 : 'NOM ->'
        for i in range(header_row):
            cell = str(top.iat[i, 0]).strip()
            m = re.match(r"^([A-Za-z0-9_]+)\s*->", cell)
            if m:
                variables.append(m.group(1))
                var_rows.append(i)

    if not variables:
        raise ValueError(
            f"Variables introuvables au-dessus de l'en-tête dans '{real_sheet}' ({path})."
        )
    return real_sheet, header_row, variables, var_rows, top


# --------------------------------------------------------------------------- #
# Modalités (code -> libellé) depuis la feuille 'Liste des variables'
# --------------------------------------------------------------------------- #

def _extract_modalities(path, variables, variables_sheet=None):
    """Renvoie {VARIABLE: {code: libellé}} pour les variables demandées."""
    if variables_sheet is None:
        variables_sheet = _find_sheet(
            path, "Liste des variables", "liste_variables", "Liste_variables",
            "Liste variables", "Variables",
        )
    raw = pd.read_excel(path, sheet_name=variables_sheet, header=None, dtype=str)
    lines = (
        raw.fillna("").astype(str)
        .agg(" ".join, axis=1)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
        .tolist()
    )

    # Correspondance tolérante : l'en-tête des données peut écrire 'AGE_4' alors
    # que la feuille des variables écrit 'AGE4' (incohérence fréquente INSEE).
    # On apparie sur le nom normalisé (majuscules, sans underscore).
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
        if _vnorm(code) in norm_to_var:   # ouverture d'une variable
            current = norm_to_var[_vnorm(code)]
        elif current is not None:         # modalité de la variable courante
            metadata[current][code] = label

    missing = [v for v in variables if not metadata[v]]
    if missing:
        raise ValueError(
            f"Aucune modalité trouvée pour {missing} dans la feuille "
            f"'{variables_sheet}' de {path}."
        )
    return metadata


# --------------------------------------------------------------------------- #
# Chargement principal
# --------------------------------------------------------------------------- #

ID_COLS = ["CODGEO", "LIBGEO"]   # colonnes identifiantes (texte) à conserver telles quelles


def _resolve_code(cell, codes_by_len):
    """Retrouve le code d'une variable dans une cellule du bloc d'en-tête.

    L'INSEE écrit parfois le code seul ('015', 'A', '1'), parfois préfixé du nom
    de la variable ('AGE400' = AGE4 + 00). On retient donc le code connu le plus
    long dont la cellule est égale OU se termine par lui.
    """
    cell = str(cell).strip()
    for c in codes_by_len:                 # déjà triés du plus long au plus court
        if cell == c or cell.endswith(c):
            return c
    return None


def load_insee_file(path, sheet: str = "COM", as_int: bool = True,
                    rename: dict | None = None) -> pd.DataFrame:
    """Charge une table INSEE BTX_TD et la renvoie en format long.

    Colonnes de sortie : CODGEO, LIBGEO, <une colonne par variable>, Nombre.

    Args:
        path: chemin du fichier .xls / .xlsx.
        sheet: feuille de données ('COM', 'ARM', '1_COM'…). Auto-tolérante.
        as_int: arrondit les effectifs à l'entier (comme les loaders 2007).
                Mets False pour garder les estimations décimales de l'INSEE.
        rename: renommage optionnel des colonnes de variables, ex.
                {'DIPL_15': 'DIPL'} pour homogénéiser entre millésimes.
    """
    real_sheet, header_row, variables, var_rows, top = _detect_structure(path, sheet)
    mapping = _extract_modalities(path, variables)
    codes_by_len = {
        v: sorted(mapping[v].keys(), key=len, reverse=True) for v in variables
    }

    df = pd.read_excel(path, sheet_name=real_sheet, header=header_row, dtype=str)
    df.columns = df.columns.astype(str).str.strip()

    sep_cols = [c for c in ID_COLS if c in df.columns]

    # Décodage par ALIGNEMENT de colonnes : pour chaque colonne de données en
    # position m, les codes des variables sont lus dans le bloc d'en-tête
    # (top.iat[ligne_variable, m]), puis résolus par suffixe. Aucune dépendance
    # à l'orthographe du nom de variable dans l'intitulé de colonne.
    frames = []
    for m, col in enumerate(df.columns):
        if col in sep_cols:
            continue
        if m >= top.shape[1]:
            raise ValueError(f"Désalignement bloc/données sur la colonne '{col}'.")

        labels = {}
        for var, vr in zip(variables, var_rows):
            code = _resolve_code(top.iat[vr, m], codes_by_len[var])
            labels[var] = mapping[var].get(code)

        sub = pd.DataFrame({c: df[c] for c in sep_cols})
        for var in variables:
            sub[var] = labels[var]            # libellé constant sur la colonne
        sub["Nombre"] = pd.to_numeric(df[col], errors="coerce")
        frames.append(sub)

    out = pd.concat(frames, ignore_index=True)
    out = out.dropna(subset=["Nombre"])
    if as_int:
        out["Nombre"] = out["Nombre"].round().astype(int)
    if rename:
        out = out.rename(columns=rename)
    return out.reset_index(drop=True)


# --------------------------------------------------------------------------- #
# Wrappers pratiques basés sur config.RAW_DATA_FILES
# --------------------------------------------------------------------------- #

# clé logique -> suffixe de clé dans RAW_DATA_FILES (config.py)
_TABLE_SUFFIX = {
    "famille": "Fam", "menage": "Men", "diplome": "Dip",
    "population": "Pop", "population2": "Pop2",
    "nationalite": "Nat", "nationalite2": "Nat2",
    "immigration": "Img", "logement": "Log", "emploi": "Emp",
}


def load_insee(year: int, table: str, sheet: str = "COM", as_int: bool = True) -> pd.DataFrame:
    """Charge une table INSEE via sa clé de config. Ex : load_insee(2013, 'diplome')."""
    if table not in _TABLE_SUFFIX:
        raise KeyError(f"Table '{table}' inconnue. Dispo : {list(_TABLE_SUFFIX)}")
    key = f"INSEE_{year}_{_TABLE_SUFFIX[table]}"
    if key not in RAW_DATA_FILES:
        raise KeyError(f"'{key}' absent de RAW_DATA_FILES (config.py).")
    return load_insee_file(RAW_DATA_FILES[key], sheet=sheet, as_int=as_int)