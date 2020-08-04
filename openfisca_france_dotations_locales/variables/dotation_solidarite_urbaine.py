from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *
import numpy as np


class indice_synthetique_dsu(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Indice synthétique DSU:\
indice synthétique pour l'éligibilité à la fraction-cible"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000038834291&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        population_dgf = commune("population_dgf", period)
        outre_mer = commune('outre_mer', period)
        potentiel_financier = commune('potentiel_financier', period)
        potentiel_financier_par_habitant = commune('potentiel_financier_par_habitant', period)
        nombre_logements = commune('nombre_logements', period)
        nombre_logements_sociaux = commune('nombre_logements_sociaux', period)
        nombre_aides_au_logement = commune('nombre_beneficiaires_aides_au_logement', period)
        revenu = commune('revenu_total', period)
        population_insee = commune('population_insee', period)
        revenu_par_habitant = commune('revenu_par_habitant', period)

        seuil_bas = parameters(period).dotation_solidarite_urbaine.eligibilite.seuil_bas_nombre_habitants
        seuil_haut = parameters(period).dotation_solidarite_urbaine.eligibilite.seuil_haut_nombre_habitants
        ratio_max_pot_fin = parameters(period).dotation_solidarite_urbaine.eligibilite.seuil_rapport_potentiel_financier
        poids_pot_fin = parameters(period).dotation_solidarite_urbaine.eligibilite.indice_synthetique.poids_potentiel_financier
        poids_logements_sociaux = parameters(period).dotation_solidarite_urbaine.eligibilite.indice_synthetique.poids_logements_sociaux
        poids_aides_au_logement = parameters(period).dotation_solidarite_urbaine.eligibilite.indice_synthetique.poids_aides_au_logement
        poids_revenu = parameters(period).dotation_solidarite_urbaine.eligibilite.indice_synthetique.poids_revenu

        groupe_bas = (~outre_mer) * (seuil_bas <= population_dgf) * (seuil_haut > population_dgf)
        groupe_haut = (~outre_mer) * (seuil_haut <= population_dgf)

        pot_fin_bas = (np.sum(groupe_bas * potentiel_financier)
                / np.sum(groupe_bas * population_dgf)) if np.sum(groupe_bas * population_dgf) > 0 else 0
        pot_fin_haut = (np.sum(groupe_haut * potentiel_financier)
                / np.sum(groupe_haut * population_dgf)) if np.sum(groupe_haut * population_dgf) > 0 else 0

        # Retrait des communes au potentiel financier trop élevé, les communes restantes ont droit à un indice synthétique
        groupe_bas_score_positif = groupe_bas * (potentiel_financier_par_habitant < ratio_max_pot_fin * pot_fin_bas)
        groupe_haut_score_positif = groupe_haut * (potentiel_financier_par_habitant < ratio_max_pot_fin * pot_fin_haut)

        # Calcul des ratios moyens nécessaires au calcul de l'indice synthétique
        part_logements_sociaux_bas = (np.sum(groupe_bas * nombre_logements_sociaux)
                / np.sum(groupe_bas * nombre_logements)) if np.sum(groupe_bas * nombre_logements) > 0 else 0
        part_logements_sociaux_haut = (np.sum(groupe_haut * nombre_logements_sociaux)
                / np.sum(groupe_haut * nombre_logements)) if np.sum(groupe_haut * nombre_logements) > 0 else 0

        part_aides_logement_bas = (np.sum(groupe_bas * nombre_aides_au_logement)
                / np.sum(groupe_bas * nombre_logements)) if np.sum(groupe_bas * nombre_logements) > 0 else 0
        part_aides_logement_haut = (np.sum(groupe_haut * nombre_aides_au_logement)
                / np.sum(groupe_haut * nombre_logements)) if np.sum(groupe_haut * nombre_logements) > 0 else 0

        revenu_moyen_bas = (np.sum(groupe_bas * revenu)
                / np.sum(groupe_bas * population_insee)) if np.sum(groupe_bas * population_insee) > 0 else 0
        revenu_moyen_haut = (np.sum(groupe_haut * revenu)
                / np.sum(groupe_haut * population_insee)) if np.sum(groupe_haut * population_insee) > 0 else 0

        part_logements_sociaux_commune = np.where(nombre_logements > 0, np.divide(nombre_logements_sociaux, nombre_logements), 0)
        part_aides_logement_commune = np.where(nombre_logements > 0, np.divide(nombre_aides_au_logement, nombre_logements), 0)

        indice_synthetique_bas = groupe_bas_score_positif * (
            poids_pot_fin * np.where(potentiel_financier_par_habitant > 0, np.divide(pot_fin_bas, potentiel_financier_par_habitant), 0)
            + poids_logements_sociaux * np.where(part_logements_sociaux_bas > 0, np.divide(part_logements_sociaux_commune, part_logements_sociaux_bas), 0)
            + poids_aides_au_logement * np.where(part_aides_logement_bas > 0, np.divide(part_aides_logement_commune, part_aides_logement_bas), 0)
            + poids_revenu * np.where(revenu_par_habitant > 0, np.divide(revenu_moyen_bas, revenu_par_habitant), 0)
            )

        indice_synthetique_haut = groupe_haut_score_positif * (
            poids_pot_fin * np.where(potentiel_financier_par_habitant > 0, np.divide(pot_fin_haut, potentiel_financier_par_habitant), 0)
            + poids_logements_sociaux * np.where(part_logements_sociaux_haut > 0, np.divide(part_logements_sociaux_commune, part_logements_sociaux_haut), 0)
            + poids_aides_au_logement * np.where(part_aides_logement_haut > 0, np.divide(part_aides_logement_commune, part_aides_logement_haut), 0)
            + poids_revenu * np.where(revenu_par_habitant > 0, np.divide(revenu_moyen_haut, revenu_par_habitant), 0)
            )
        return indice_synthetique_bas + indice_synthetique_haut


class rang_indice_synthetique_dsu_seuil_haut(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Rang indice synthétique DSU seuil haut:\
Rang de classement de l'indice synthétique de DSU pour les communes de plus de 10000 habitants"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000038834291&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        seuil_haut = parameters(period).dotation_solidarite_urbaine.eligibilite.seuil_haut_nombre_habitants
        indice_synthetique_dsu = commune('indice_synthetique_dsu', period)
        population_dgf = commune('population_dgf', period)
        # L'utilisation d'un double argsort renvoie un tableau qui contient
        # la statistique d'ordre (indexée par 0) du tableau d'entrée dans
        # l'ordre croissant (cf par exemple
        # https://www.berkayantmen.com/rank.html).
        # On l'applique sur l'opposé de l'indice synthétique
        # pour obtenir un classement dans l'ordre décroissant.
        # les communes de même indice synthétique auront un rang différent (non spécifié par la loi)
        score_a_classer = (indice_synthetique_dsu) * (seuil_haut <= population_dgf)
        return (-score_a_classer).argsort().argsort()


class rang_indice_synthetique_dsu_seuil_bas(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Rang indice synthétique DSU seuil bas:\
Rang de classement de l'indice synthétique de DSU pour les communes de plus de 5000 à 9999 habitants"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000038834291&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        seuil_bas = parameters(period).dotation_solidarite_urbaine.eligibilite.seuil_bas_nombre_habitants
        seuil_haut = parameters(period).dotation_solidarite_urbaine.eligibilite.seuil_haut_nombre_habitants
        indice_synthetique_dsu = commune('indice_synthetique_dsu', period)
        population_dgf = commune('population_dgf', period)
        # L'utilisation d'un double argsort renvoie un tableau qui contient
        # la statistique d'ordre (indexée par 0) du tableau d'entrée dans
        # l'ordre croissant (cf par exemple
        # https://www.berkayantmen.com/rank.html).
        # On l'applique sur l'opposé de l'indice synthétique
        # pour obtenir un classement dans l'ordre décroissant.
        # les communes de même indice synthétique auront un rang différent (non spécifié par la loi)
        score_a_classer = (indice_synthetique_dsu) * (seuil_haut > population_dgf) * (seuil_bas <= population_dgf)
        return (-score_a_classer).argsort().argsort()


class dsu_nombre_communes_eligibles_seuil_bas(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Nombres de communes du seuil bas éligible à la DSU:\
Nombre de communes éligibles à la dsu dans le seuil bas"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000038834291&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        population_dgf = commune("population_dgf", period)
        outre_mer = commune('outre_mer', period)

        seuil_bas = parameters(period).dotation_solidarite_urbaine.eligibilite.seuil_bas_nombre_habitants
        seuil_haut = parameters(period).dotation_solidarite_urbaine.eligibilite.seuil_haut_nombre_habitants
        pourcentage_eligible_bas = parameters(period).dotation_solidarite_urbaine.eligibilite.part_eligible_seuil_bas

        nombre_communes_seuil_bas = ((~outre_mer) * (population_dgf >= seuil_bas) * (population_dgf < seuil_haut)).sum()

        return int(nombre_communes_seuil_bas * pourcentage_eligible_bas + 0.9999)


class dsu_nombre_communes_eligibles_seuil_haut(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Nombres de communes du seuil haut éligible à la DSU:\
Nombre de communes éligibles à la dsu dans le seuil haut"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000038834291&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        population_dgf = commune("population_dgf", period)
        outre_mer = commune('outre_mer', period)

        seuil_haut = parameters(period).dotation_solidarite_urbaine.eligibilite.seuil_haut_nombre_habitants
        pourcentage_eligible_haut = parameters(period).dotation_solidarite_urbaine.eligibilite.part_eligible_seuil_haut

        nombre_communes_seuil_haut = ((~outre_mer) * (population_dgf >= seuil_haut)).sum()

        return int(nombre_communes_seuil_haut * pourcentage_eligible_haut + 0.9999)


class dsu_eligible(Variable):
    value_type = bool
    entity = Commune
    definition_period = YEAR
    label = "DSU Eligible:\
Est éligible à la dotation de solidarité urbaine "
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000038834291&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        indice_synthetique_dsu = commune('indice_synthetique_dsu', period)
        rang_indice_synthetique_dsu_seuil_bas = commune('rang_indice_synthetique_dsu_seuil_bas', period)
        rang_indice_synthetique_dsu_seuil_haut = commune('rang_indice_synthetique_dsu_seuil_haut', period)

        nombre_elig_seuil_bas = commune('dsu_nombre_communes_eligibles_seuil_bas', period)
        nombre_elig_seuil_haut = commune('dsu_nombre_communes_eligibles_seuil_haut', period)
        elig_seuil_bas = (indice_synthetique_dsu > 0) * (rang_indice_synthetique_dsu_seuil_bas < nombre_elig_seuil_bas)
        elig_seuil_haut = (indice_synthetique_dsu > 0) * (rang_indice_synthetique_dsu_seuil_haut < nombre_elig_seuil_haut)
        return elig_seuil_bas | elig_seuil_haut


class dsu_montant_total(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "DSU Montant hors garanties:\
Valeur totale attribuée (hors garanties) aux communes éligibles à la DSU"
    reference = "https://www.collectivites-locales.gouv.fr/files/files/dgcl_v2/FLAE/Circulaires_2019/note_dinformation_2019_dsu.pdf"
    documentation = '''
    La somme effectivement mise en répartition au profit des
    communes de métropole s'élève à 2164552909 €
    '''
    # Devrait peut-être être un paramètre

    def formula_2018_01(commune, period, parameters):
        montant_total_a_attribuer = 2_079_328_714
        return montant_total_a_attribuer

    def formula_2019_01(commune, period, parameters):
        montant_total_a_attribuer = 2_164_552_909
        return montant_total_a_attribuer


class dsu_montant_garantie_pluriannuelle(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "DSU Montant garanti au titre des années N-2 ou antérieures:\
Montant de la garantie pluriannuelle touchée par la commune en cas de non-éligibilité"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033814534&cidTexte=LEGITEXT000006070633"
    documentation = """Lorsqu'une commune cesse d'être éligible à la dotation à la suite
    d'une baisse de sa population en deçà du seuil minimal fixé au 2° de l'article
    L. 2334-16, elle perçoit, à titre de garantie pour les neufs exercices suivants,
    une attribution calculée en multipliant le montant de dotation perçu la dernière
    année où la commune était éligible par un coefficient égal à 90 % la première
    année et diminuant ensuite d'un dixième chaque année.

    En outre, lorsque, à compter de 2000, une commune, dont l'établissement public de
    coopération intercommunale dont elle est membre a opté deux ans auparavant pour
    l'application du régime fiscal prévu à l'article 1609 nonies C du code général des
    impôts, cesse d'être éligible à la dotation du fait de l'application des 1 et 2 du
    II de l'article L2334-4, elle perçoit, pendant cinq ans, une attribution calculée
    en multipliant le montant de dotation perçu la dernière année où la commune était
    éligible par un coefficient égal à 90 % la première année et diminuant ensuite d'un
    dixième chaque année. """

# Bon OK peut être je dis bien peut-être que je peux :
# prendre montant total à attribuer
# trouver somehow le montant des garanties du futur
# retirer ce montant des garanties
# retirer le montant des dotations spontanées


class dsu_montant_garantie_annuelle(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "DSU Montant garanti au titre de l'année N-1:\
Montant garanti en cas de non éligibilité pour les communes non éligibles"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033814534&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        montant_eligible_an_dernier = commune('dsu_montant_eligible', period.last_year)
        part_garantie = 0.5
        return part_garantie * montant_eligible_an_dernier


class dsu_montant_garantie_non_eligible(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "DSU Montant garanti non éligible:\
Montant de la garantie de DSU versée aux communes non éligibles"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033814534&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        dsu_montant_garantie_annuelle = commune('dsu_montant_garantie_annuelle', period)
        dsu_montant_garantie_pluriannuelle = commune('dsu_montant_garantie_pluriannuelle', period)
        dsu_eligible = commune('dsu_eligible', period)
        return (~dsu_eligible) * max_(dsu_montant_garantie_annuelle, dsu_montant_garantie_pluriannuelle)


class dsu_montant_total_eligibles(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "DSU Montant hors garanties:\
Valeur totale attribuée (hors garanties) aux communes éligibles à la DSU"
    reference = "https://www.collectivites-locales.gouv.fr/files/files/dgcl_v2/FLAE/Circulaires_2019/note_dinformation_2019_dsu.pdf"

    def formula_2019_01(commune, period, parameters):
        dsu_montant_total = commune('dsu_montant_total', period)
        dsu_montant_garantie_non_eligible = commune('dsu_montant_garantie_non_eligible', period)
        # retrait des montants garantis, le reste est à distribuer entre communes éligibles
        return dsu_montant_total - sum(dsu_montant_garantie_non_eligible)


class dsu_montant_eligible(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "DSU au titre de l'éligibilité:\
Montant total reçu par la commune au titre de son éligibilité à la DSU (incluant part spontanée et augmentation)"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033814543&cidTexte=LEGITEXT000006070633"
