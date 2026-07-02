
import numpy as np
import pandas as pd


def _codgeo(dept, com):
    d, c = str(dept).strip(), str(com).strip()
    if d in ("2A", "2B"):
        return d + c.zfill(3)
    if d.startswith(("97", "98")) and len(d) == 3:   # DOM : dept 3 + commune 2
        return d + c.zfill(2)
    return d.zfill(2) + c.zfill(3)                     # métropole : dept 2 + commune 3


def _commune_abstention(bureaux, cod_dept, cod_com, inscrits, abst=None, votants=None):
    """bureaux : DataFrame déjà dédoublonnée au niveau bureau. Agrège par commune."""
    b = bureaux.copy()
    b["CODGEO"] = [_codgeo(d, c) for d, c in zip(b[cod_dept], b[cod_com])]
    b[inscrits] = pd.to_numeric(b[inscrits], errors="coerce")
    if abst is not None:
        b["_abs"] = pd.to_numeric(b[abst], errors="coerce")
    else:
        b["_abs"] = b[inscrits] - pd.to_numeric(b[votants], errors="coerce")
    g = b.groupby("CODGEO").agg(inscrits=(inscrits, "sum"), abstentions=("_abs", "sum")).reset_index()
    g["taux_abstention"] = g["abstentions"] / g["inscrits"]
    return g


def charger_abstention(annee, chemin):
    """Renvoie une table communale : CODGEO, inscrits, abstentions, taux_abstention (1er tour)."""
    if annee == 2014:
        df = pd.read_csv(chemin, sep=";", encoding="latin-1", dtype=str)
        df.columns = [c.strip() for c in df.columns]
        df = df[df["N° tour"] == "1"]
        bur = df.drop_duplicates(["Code département", "Code commune", "N° de bureau de vote"])
        return _commune_abstention(bur, "Code département", "Code commune", "Inscrits", votants="Votants")

    if annee == 2020:
        df = pd.read_excel(chemin, dtype=str)          # fichier 1er tour
        df.columns = [str(c).strip() for c in df.columns]
        bur = df.drop_duplicates(["Code du département", "Code de la commune", "Code B.Vote"])
        return _commune_abstention(bur, "Code du département", "Code de la commune", "Inscrits", abst="Abstentions")

    if annee == 2008:
        # Fichier 2008 « sale » (nb de colonnes variable : ';' dans les noms).
        # On lit ligne à ligne les 8 premiers champs (avant les noms de candidats).
        # 0 Date | 1 Code dept | 2 Lib dept | 3 Code com | 4 Lib com | 5 Bureau | 6 Inscrits | 7 Abstentions
        recs = []
        with open(chemin, encoding="latin-1") as fh:
            next(fh)                                    # en-tête
            for line in fh:
                p = line.rstrip("\n").split(";")
                if len(p) < 8:
                    continue
                recs.append((p[1], p[3], p[5], p[6], p[7]))
        bur = pd.DataFrame(recs, columns=["dept", "com", "bvote", "Inscrits", "Abstentions"])
        bur = bur.drop_duplicates(["dept", "com", "bvote"])
        # NB : les DOM sont codés ZA/ZB… en 2008 -> non appariables aux CODGEO 97x (métropole OK).
        return _commune_abstention(bur, "dept", "com", "Inscrits", abst="Abstentions")

    raise ValueError(f"Année non gérée : {annee}")
