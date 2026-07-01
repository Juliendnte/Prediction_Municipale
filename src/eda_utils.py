"""Utilitaires EDA partagés par les notebooks par millésime et le notebook d'évolution."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

GEO = ["CODGEO", "DEP", "annee"]


def colonnes_num(F):
    return [c for c in F.columns if c not in GEO]


def diagnostics(F):
    """Affiche dimensions, types, manquants, doublons, cohérence géo, aberrants."""
    num = colonnes_num(F)
    print("Dimensions :", F.shape)
    print("Types :", dict(F.dtypes.value_counts().astype(int)))
    print("Doublons CODGEO :", int(F["CODGEO"].duplicated().sum()))
    print("CODGEO ≠ 5 caractères :", int((F["CODGEO"].str.len() != 5).sum()))
    print("Communes population = 0 :", int((F["population"] == 0).sum()))
    print("Départements :", F["DEP"].nunique())
    na = F[num].isna().sum()
    print("\nManquants (colonnes concernées) :")
    print(na[na > 0].sort_values(ascending=False).to_string() if na.sum() else "  aucun")

    def taux_aberrants(s):
        s = s.dropna(); q1, q3 = s.quantile([.25, .75]); iqr = q3 - q1
        return ((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).mean() * 100
    ab = pd.Series({c: taux_aberrants(F[c]) for c in num}).sort_values(ascending=False)
    print("\n% communes aberrantes (IQR) — top 8 :")
    print(ab.head(8).round(1).to_string())


def nettoyer(F):
    """Retire les communes vides, impute par médiane départementale, ajoute des variables dérivées."""
    num = colonnes_num(F)
    clean = F[F["population"] > 0].copy()
    for c in num:
        clean[c] = clean.groupby("DEP")[c].transform(lambda s: s.fillna(s.median()))
        clean[c] = clean[c].fillna(clean[c].median())
    clean["pop_log"]               = np.log1p(clean["population"])
    clean["indice_vieillissement"] = clean["part_65plus"] / clean["part_moins15"].replace(0, np.nan)
    clean["part_classes_pop"]      = clean["part_ouvriers"] + clean["part_employes"]
    clean["part_classes_sup"]      = clean["part_cadres"] + clean["part_prof_inter"]
    clean["indice_vieillissement"] = clean["indice_vieillissement"].replace([np.inf, -np.inf], np.nan)
    clean["indice_vieillissement"] = clean["indice_vieillissement"].fillna(clean["indice_vieillissement"].median())
    return clean


def paires_correlees(clean, seuil=0.8):
    num = [c for c in clean.columns if c not in GEO]
    corr = clean[num].corr().abs()
    res = [(corr.index[i], corr.columns[j], round(corr.iat[i, j], 2))
           for i in range(len(corr)) for j in range(i + 1, len(corr)) if corr.iat[i, j] > seuil]
    return sorted(res, key=lambda x: -x[2])


# ---------- visualisations ----------
def plot_histogrammes(clean, cols):
    n = len(cols); ncols = 4; nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.2 * ncols, 3 * nrows))
    for ax, c in zip(np.array(axes).flat, cols):
        ax.hist(clean[c], bins=50, color="#3b6fb6"); ax.set_title(c, fontsize=9)
    for ax in np.array(axes).flat[n:]:
        ax.axis("off")
    fig.tight_layout(); plt.show()


def plot_boxplots(clean, cols):
    fig, ax = plt.subplots(figsize=(1.1 * len(cols) + 2, 5))
    ax.boxplot([clean[c] for c in cols], tick_labels=cols,
               flierprops=dict(marker=".", markersize=2, alpha=.3))
    ax.set_xticklabels(cols, rotation=35, ha="right"); ax.set_title("Boxplots des parts communales")
    fig.tight_layout(); plt.show()


def plot_communes_par_dep(clean):
    fig, ax = plt.subplots(figsize=(17, 4))
    clean["DEP"].value_counts().sort_index().plot.bar(ax=ax, color="#4a8")
    ax.set_title("Nombre de communes par département"); fig.tight_layout(); plt.show()


def plot_heatmap(clean, cols, titre="Matrice de corrélation"):
    corr = clean[cols].corr()
    fig, ax = plt.subplots(figsize=(0.7 * len(cols) + 2, 0.7 * len(cols) + 1))
    im = ax.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(cols))); ax.set_yticklabels(cols, fontsize=8)
    for i in range(len(cols)):
        for j in range(len(cols)):
            ax.text(j, i, f"{corr.iat[i, j]:.1f}", ha="center", va="center", fontsize=6,
                    color="white" if abs(corr.iat[i, j]) > 0.6 else "black")
    fig.colorbar(im, fraction=0.046); ax.set_title(titre); fig.tight_layout(); plt.show()


# ---------- analyse sociologique / territoriale ----------
STRATE_BINS = [0, 2000, 10000, 50000, np.inf]
STRATE_LABELS = ["Rural (<2k)", "Petite ville (2-10k)", "Ville moyenne (10-50k)", "Grande ville (>50k)"]

def stratifier(clean):
    """Ajoute une colonne 'strate' urbaine (proxy d'urbanité par la population)."""
    clean = clean.copy()
    clean["strate"] = pd.cut(clean["population"], bins=STRATE_BINS, labels=STRATE_LABELS)
    return clean

def profil_strate(clean, cols, pondere=True):
    """Profil moyen (pondéré population par défaut) par strate urbaine."""
    def agg(g):
        if pondere:
            return pd.Series({c: np.average(g[c], weights=g["population"]) for c in cols})
        return g[cols].mean()
    return clean.groupby("strate", observed=True).apply(agg, include_groups=False)

FEAT_CLUSTER = ["pop_log","taux_chomage","part_sup","part_cadres","part_ouvriers","part_65plus",
                "part_moins15","part_proprietaires","part_loc_hlm","part_etrangers",
                "part_menages_1pers","sect_agriculture","sect_tertiaire"]

def typologie(clean, feat=None, k=5, random_state=0):
    """K-means sur variables standardisées. Renvoie (clean+cluster, profil des clusters)."""
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    feat = feat or FEAT_CLUSTER
    clean = clean.copy()
    X = StandardScaler().fit_transform(clean[feat])
    clean["cluster"] = KMeans(n_clusters=k, random_state=random_state, n_init=10).fit_predict(X)
    synth = ["taux_chomage","part_sup","part_cadres","part_ouvriers","part_65plus",
             "part_proprietaires","part_loc_hlm","part_etrangers","sect_agriculture"]
    prof = clean.groupby("cluster")[synth].mean()
    prof["pop_med"] = clean.groupby("cluster")["population"].median()
    prof["n"] = clean.groupby("cluster").size()
    return clean, prof

def indice_vulnerabilite_abstention(clean):
    """Indice illustratif (hypothèse) : cumul de facteurs associés à une participation plus faible."""
    z = lambda s: (s - s.mean()) / s.std()
    return (z(clean["taux_chomage"]) + z(clean["part_loc_hlm"]) + z(clean["part_menages_1pers"])
            + z(clean["part_sans_diplome"]) - z(clean["part_65plus"]) - z(clean["part_proprietaires"]))