Ceci est un projet de ML pour prédire les élections municipales 2026

L'ia va être entrainée sur des données historiques (2008 - 2020) de résultats d'élections municipales pour apprendre à prédire les résultats des élections 2026.

Nous irons ensuite comparer les résultats prédits avec les résultats réels pour évaluer la performance de notre modèle.

Sur le site :
Il y aura une carte de la France découpé pour chaque municipalité avec une couleur représentant le résultat prédit par notre modèle. (Droite = bleu, Gauche = rouge)
Quand une municipalité est cliquée, un écran à droite de la carte montrera des statistiques sur la municipalité ainsi que les résultats prédits et réels.
Nous verrons aussi des analyses intéressantes éffectué pendant la conception du model.
Ainsi que des chiffres clés comme le nombre d'abstentions, le taux de participation et le pourcentage de voix pour chaque parti politique, etc.

Nos BDD :
https://www.data.gouv.fr/datasets/elections-municipales-2001-resultats-572156 - Résultats des élections municipales de 2001
https://www.data.gouv.fr/datasets/elections-municipales-2008-communes-de-plus-de-3-500-habitants-resultats-par-bureaux-de-vote-1 - Résultats des élections municipales de 2008
https://www.data.gouv.fr/datasets/elections-municipales-2014-resultats-par-bureaux-de-vote - Résultats des élections municipales de 2014
https://www.data.gouv.fr/datasets/elections-municipales-2020-resultats-1er-tour - Résultats des élections municipales du 1er tour de 2020
https://www.data.gouv.fr/datasets/municipales-2020-resultats-2nd-tour - Résultats des élections municipales du 2nd tour de 2020
https://www.data.gouv.fr/datasets/repertoire-national-des-elus-1 - Répertoire national des élus (Pas utile car que 2020)
https://catalogue-donnees.insee.fr/fr/explorateur/DS_POPULATIONS_HISTORIQUES - Données démographiques historiques (1968 à 2023)
https://www.data.gouv.fr/datasets/donnees-des-elections-agregees - Nuances Politiques
https://object.files.data.gouv.fr/data-pipeline-open/elections/general_results.csv - Stat sur les votes (Peut être utile ou non)