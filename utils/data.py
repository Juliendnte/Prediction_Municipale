"""
Couche de données — pour l'instant des valeurs statiques cohérentes avec la
maquette Stitch fournie. À remplacer par de vrais chargements (CSV INSEE,
résultats électoraux, modèle ML) au fur et à mesure de la construction des
pages suivantes. Garder cette interface stable permet aux pages de ne pas
changer quand la source de données change.
"""

from dataclasses import dataclass


@dataclass
class HomeKPIs:
    communes_analysees: int
    participation_moyenne: float
    total_listes: int
    periode_min: int
    periode_max: int


def get_home_kpis() -> HomeKPIs:
    return HomeKPIs(
        communes_analysees=34945,
        participation_moyenne=64.5,
        total_listes=12450,
        periode_min=2001,
        periode_max=2026,
    )


def get_participation_trend() -> list[dict]:
    """Série simplifiée de la participation moyenne nationale par scrutin municipal."""
    return [
        {"annee": 2001, "participation": 67.1},
        {"annee": 2008, "participation": 66.5},
        {"annee": 2014, "participation": 63.5},
        {"annee": 2020, "participation": 58.6},
        {"annee": 2026, "participation": 60.2},  # projection
    ]


def get_political_distribution() -> list[dict]:
    return [
        {"bloc": "Extrême gauche - Gauche", "valeur": 28},
        {"bloc": "Centre - Majorité", "valeur": 35},
        {"bloc": "Droite - Républicains", "valeur": 22},
        {"bloc": "Extrême droite", "valeur": 15},
    ]


def get_home_highlights() -> list[dict]:
    """Cartes d'accroche qui annoncent les modules de l'app (mappées sur les pages 2-7)."""
    return [
        {
            "icon": "map",
            "title": "Carte municipale interactive",
            "text": (
                "Explorez les résultats commune par commune sur trois scrutins "
                "(2008, 2014, 2020) avec les indicateurs INSEE associés."
            ),
        },
        {
            "icon": "group_work",
            "title": "Segmentation -1000 / +1000 habitants",
            "text": (
                "Comparez les dynamiques électorales selon la taille des communes "
                "pour révéler des logiques structurelles."
            ),
        },
        {
            "icon": "query_stats",
            "title": "Modélisation prédictive",
            "text": (
                "Un modèle entraîné sur 25 ans de scrutins municipaux pour anticiper "
                "les tendances de 2026, présenté en toute transparence."
            ),
        },
    ]