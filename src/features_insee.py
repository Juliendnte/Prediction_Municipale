"""Construit une table communale numérique (1 ligne/commune) à partir des
tableaux détaillés INSEE en format long. Variables = parts de profils + taux."""
import numpy as np
import pandas as pd


def _pop(df):
    """Population totale (somme des effectifs) par commune."""
    return df.groupby("CODGEO", observed=True)["Nombre"].sum()


def _part(df, var, predicate):
    """Part (0-1) des modalités de `var` vérifiant predicate(label), par commune."""
    sub = df[df[var].map(lambda x: predicate(str(x)) if pd.notna(x) else False)]
    num = sub.groupby("CODGEO", observed=True)["Nombre"].sum()
    den = _pop(df)
    return (num.reindex(den.index, fill_value=0) / den).rename(None)


def _dep_from_codgeo(codgeo):
    c = str(codgeo)
    return c[:3] if c[:2] in ("97", "98") else c[:2]


def construire_features(dfs, annee):
    """dfs : dict {nom_table: df_long}. Renvoie une DataFrame (1 ligne/commune).

    Tolérant : que les colonnes soient brutes (DIPL_19, AGE_4) ou renommées
    (DIPL, AGE4), le résultat est identique.
    """
    _ren = {"DIPL_15": "DIPL", "DIPL_19": "DIPL", "AGE_4": "AGE4"}

    def _norm_codgeo(s):
        s = str(s).split(".")[0].strip()      # gère un éventuel '1001.0' (float)
        return s.zfill(5) if s[:2] not in ("2A", "2B") and len(s) < 5 else s

    dfs = {k: v.rename(columns=_ren).assign(CODGEO=v["CODGEO"].map(_norm_codgeo))
           for k, v in dfs.items()}

    f = pd.DataFrame(index=_pop(dfs["nationalite"]).index)  # NAT1 = toute la population
    f.index.name = "CODGEO"

    # --- Démographie (NAT1 : tous âges) ---
    nat = dfs["nationalite"]
    f["population"]      = _pop(nat)
    f["part_moins15"]    = _part(nat, "AGE4", lambda s: ("Moins de 15" in s) or s.startswith("0 "))
    f["part_15_24"]      = _part(nat, "AGE4", lambda s: s.startswith("15"))
    f["part_25_54"]      = _part(nat, "AGE4", lambda s: s.startswith("25"))
    f["part_55plus"]     = _part(nat, "AGE4", lambda s: s.startswith("55"))
    f["part_etrangers"]  = _part(nat, "INATC", lambda s: "tranger" in s)

    # --- Activité / chômage (POP5 : 15 ans et +) ---
    pop = dfs["population"]
    actifs_occ = _part(pop, "TACTR", lambda s: "ayant un emploi" in s)
    chomeurs   = _part(pop, "TACTR", lambda s: s.strip() == "Chômeurs")
    f["taux_chomage"]   = chomeurs / (actifs_occ + chomeurs)
    f["taux_activite"]  = actifs_occ + chomeurs
    f["part_retraites"] = _part(pop, "TACTR", lambda s: "etrait" in s)
    f["part_etudiants"] = _part(pop, "TACTR", lambda s: "tudiant" in s)
    f["part_65plus"]    = _part(pop, "AGEQ65", lambda s: "65 ans ou plus" in s)

    # --- Diplôme (FOR2) — libellés tolérants 2007/2013/2019 (nomenclatures différentes) ---
    dip = dfs["diplome"]
    f["part_sans_diplome"] = _part(dip, "DIPL", lambda s: ("Aucun" in s) or ("Pas de scolarité" in s)
                                                          or (s.strip() == "Certificat d'études primaires"))
    f["part_cap_bep"]      = _part(dip, "DIPL", lambda s: ("CAP" in s) or ("aptitudes professionnelles" in s)
                                                          or ("études professionnelles" in s) or ("BEP" in s))
    f["part_bac"]          = _part(dip, "DIPL", lambda s: s.startswith("Bac"))
    f["part_sup"]          = _part(dip, "DIPL", lambda s: ("supérieur" in s) or ("universitaire" in s)
                                                          or ("BTS" in s) or ("DUT" in s))
    f["part_bac5plus"]     = _part(dip, "DIPL", lambda s: ("bac + 5" in s) or ("3ème cycle" in s))

    # --- CSP (POP6 : CS1_8) ---
    p6 = dfs["population2"]
    f["part_cadres"]      = _part(p6, "CS1_8", lambda s: "Cadres" in s)
    f["part_prof_inter"]  = _part(p6, "CS1_8", lambda s: "intermédiaires" in s)
    f["part_employes"]    = _part(p6, "CS1_8", lambda s: "Employés" in s)
    f["part_ouvriers"]    = _part(p6, "CS1_8", lambda s: "Ouvriers" in s)
    f["part_agriculteurs"]= _part(p6, "CS1_8", lambda s: "Agriculteurs" in s)
    f["part_artisans"]    = _part(p6, "CS1_8", lambda s: "Artisans" in s)

    # --- Secteurs (EMP3 : NA5) ---
    emp = dfs["emploi"]
    f["sect_agriculture"] = _part(emp, "NA5", lambda s: "Agriculture" in s)
    f["sect_industrie"]   = _part(emp, "NA5", lambda s: "Industrie" in s)
    f["sect_construction"]= _part(emp, "NA5", lambda s: "Construction" in s)
    f["sect_tertiaire"]   = _part(emp, "NA5", lambda s: ("Commerce" in s) or ("Administration" in s))

    # --- Ménages (MEN1 : NPERC) ---
    men = dfs["menage"]
    f["part_menages_1pers"] = _part(men, "NPERC", lambda s: s.startswith("1 "))
    chiffre = lambda s: int(s.strip()[0])
    g = men.groupby(["CODGEO", "NPERC"], observed=True)["Nombre"].sum().reset_index()
    g["taille"] = g["NPERC"].map(lambda s: chiffre(str(s)))
    f["taille_moy_menage"] = (g.assign(p=g["taille"] * g["Nombre"])
                                .groupby("CODGEO")["p"].sum() /
                              g.groupby("CODGEO")["Nombre"].sum())

    # --- Familles (FAM4 : NBENFFR) ---
    fam = dfs["famille"]
    f["part_fam_sans_enfant"] = _part(fam, "NBENFFR", lambda s: "Aucun enfant" in s)
    f["part_fam_nombreuses"]  = _part(fam, "NBENFFR", lambda s: s.strip()[0] in ("3", "4"))

    # --- Logement (PRINC14 : STOCD) ---
    log = dfs["logement"]
    f["part_proprietaires"] = _part(log, "STOCD", lambda s: s.strip() == "Propriétaire")
    f["part_loc_hlm"]       = _part(log, "STOCD", lambda s: "HLM" in s)
    f["part_loc_prive"]     = _part(log, "STOCD", lambda s: "non HLM" in s)

    # --- Géographie ---
    f = f.reset_index()
    f["DEP"] = f["CODGEO"].map(_dep_from_codgeo)
    f["annee"] = annee
    return f


# --- Chargement unifié des 3 millésimes via le moteur auto-descriptif --------
_TABLES = {"famille": "Fam", "menage": "Men", "diplome": "Dip", "population": "Pop",
           "population2": "Pop2", "nationalite": "Nat", "logement": "Log", "emploi": "Emp"}

def charger_tables(annee, raw_data_files=None):
    """Charge les 8 tables d'un millésime en format long (même moteur pour 2007/2013/2019).

    raw_data_files : dict des chemins (RAW_DATA_FILES de config). Si None, tente l'import.
    """
    try:
        from .insee_loader import load_insee_file
    except ImportError:
        try:
            from insee_loader import load_insee_file
        except ImportError:
            from src.insee_loader import load_insee_file
    if raw_data_files is None:
        try:
            from .config import RAW_DATA_FILES as raw_data_files
        except ImportError:
            try:
                from src.config import RAW_DATA_FILES as raw_data_files
            except ImportError:
                from config import RAW_DATA_FILES as raw_data_files
    dfs = {}
    for nom, suf in _TABLES.items():
        path = raw_data_files[f"INSEE_{annee}_{suf}"]
        sheet = "2_COM" if (annee == 2007 and nom == "emploi") else "COM"
        dfs[nom] = load_insee_file(path, sheet)
    return dfs