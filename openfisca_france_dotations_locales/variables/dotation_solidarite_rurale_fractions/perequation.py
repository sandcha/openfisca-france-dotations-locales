from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *
import numpy as np

class dsr_eligible_fraction_perequation(Variable):
    value_type = bool
    entity = Commune
    definition_period = YEAR
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
    documentation = '''
        La deuxième fraction de la dotation de solidarité rurale est attribuée
        aux communes de moins de 10 000 habitants dont le potentiel financier par habitant
        est inférieur au double du potentiel financier moyen par habitant
        des communes appartenant à la même strate démographique.
        La population à prendre en compte est également la population DGF 2019.
    '''

    def formula(commune, period, parameters):
        seuil_nombre_habitants = parameters(period).dotation_solidarite_rurale.seuil_nombre_habitants
        population_dgf = commune('population_dgf', period)

        potentiel_financier_par_habitant = commune('potentiel_financier_par_habitant', period)
        potentiel_financier_par_habitant_strate = commune('potentiel_financier_par_habitant_moyen', period)

        plafond = 2 * potentiel_financier_par_habitant_strate
        outre_mer = commune('outre_mer', period)
        return (~outre_mer) * (population_dgf < seuil_nombre_habitants) * (potentiel_financier_par_habitant <= plafond)


class dsr_montant_total_eligibles_fraction_perequation(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant disponible pour communes éligibles DSR fraction bourg-centre"
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"

    def formula(commune, period, parameters):
        montant_total_a_attribuer = 645_050_872 - 7_403_123
        # montant inscrit dans la note. Pour le transformer en formule il faut
        # que soient implémentés :
        # les formules de garanties pour communes nouvellement non éligibles (moyen)
        # les garanties communes nouvelles (chaud)
        # la répartition du montant global vers la DSR (très difficile)
        return montant_total_a_attribuer


class dsr_montant_total_eligibles_fraction_perequation_part_potentiel_financier_par_habitant(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant total DSR fraction péréquation - potentiel financier par habitant:\
Valeur totale attribuée (hors garanties de stabilité) aux communes éligibles à la fraction péréquation de la DSR au titre du potentiel financier par habitant"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433094&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        poids = parameters(period).dotation_solidarite_rurale.attribution.poids_potentiel_financier_par_habitant
        return commune('dsr_montant_total_eligibles_fraction_perequation', period) * poids


class dsr_montant_total_eligibles_fraction_perequation_part_longueur_voirie(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant total DSR fraction péréquation - longueur voirie:\
Valeur totale attribuée (hors garanties de stabilité) aux communes éligibles à la fraction péréquation de la DSR au titre de la longueur de voirie"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433094&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        poids = parameters(period).dotation_solidarite_rurale.attribution.poids_longueur_voirie
        return commune('dsr_montant_total_eligibles_fraction_perequation', period) * poids


class dsr_montant_total_eligibles_fraction_perequation_part_enfants(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant total DSR fraction péréquation - nombre d'enfants:\
Valeur totale attribuée (hors garanties de stabilité) aux communes éligibles à la fraction péréquation de la DSR au titre du nombre d'enfants"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433094&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        poids = parameters(period).dotation_solidarite_rurale.attribution.poids_enfants
        return commune('dsr_montant_total_eligibles_fraction_perequation', period) * poids


class dsr_montant_total_eligibles_fraction_perequation_part_potentiel_financier_par_hectare(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant total DSR fraction péréquation - potentiel financier par hectare:\
Valeur totale attribuée (hors garanties de stabilité) aux communes éligibles à la fraction péréquation de la DSR au titre du potentiel financier par hectare"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433094&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        poids = parameters(period).dotation_solidarite_rurale.attribution.poids_potentiel_financier_par_hectare
        return commune('dsr_montant_total_eligibles_fraction_perequation', period) * poids


class dsr_score_attribution_perequation_part_potentiel_financier_par_habitant(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Score DSR fraction péréquation - potentiel financier par habitant:\
Score d'attribution de la fraction péréquation de la DSR au titre du potentiel financier par habitant"
    reference = ["https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433094&cidTexte=LEGITEXT000006070633",
            "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"]
    documentation = """1° Pour 30 % de son montant, en fonction de la population
    pondérée par l'écart entre le potentiel financier par habitant de la
    commune et le potentiel financier moyen par habitant des communes
    appartenant au même groupe démographique ainsi que par l'effort fiscal
    plafonné à 1,2 ;"""

    def formula(commune, period, parameters):
        potentiel_financier_par_habitant = commune('potentiel_financier_par_habitant', period)
        potentiel_financier_par_habitant_strate = commune('potentiel_financier_par_habitant_moyen', period)
        effort_fiscal = commune('effort_fiscal', period)
        dsr_eligible_fraction_perequation = commune("dsr_eligible_fraction_perequation", period)
        population_dgf = commune('population_dgf', period)

        plafond_effort_fiscal = parameters(period).dotation_solidarite_rurale.attribution.plafond_effort_fiscal

        facteur_pot_fin = 2 - potentiel_financier_par_habitant / potentiel_financier_par_habitant_strate
        facteur_effort_fiscal = np.minimum(plafond_effort_fiscal, effort_fiscal)

        return dsr_eligible_fraction_perequation * population_dgf * facteur_pot_fin * facteur_effort_fiscal


class dsr_score_attribution_perequation_part_longueur_voirie(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Score DSR fraction péréquation - longueur voirie:\
Score d'attribution de la fraction péréquation de la DSR au titre de la voirie"
    reference = ["https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433094&cidTexte=LEGITEXT000006070633",
            "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"]
    documentation = """2° Pour 30 % de son montant, proportionnellement à la longueur
    de la voirie classée dans le domaine public communal ; pour les communes situées
    en zone de montagne ou pour les communes insulaires, la longueur de la voirie est
    doublée. Pour l'application du présent article, une commune insulaire s'entend
    d'une commune de métropole située sur une île qui, n'étant pas reliée au continent
    par une infrastructure routière, comprend une seule commune ou un seul
    établissement public de coopération intercommunale
    """

    def formula(commune, period, parameters):
        longueur_voirie = commune('longueur_voirie', period)
        zone_de_montagne = commune('zone_de_montagne', period)
        dsr_eligible_fraction_perequation = commune("dsr_eligible_fraction_perequation", period)
        insulaire = commune('insulaire', period)

        return dsr_eligible_fraction_perequation * longueur_voirie * np.where(insulaire | zone_de_montagne, 2, 1)


class dsr_score_attribution_perequation_part_enfants(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Score DSR fraction péréquation - enfants:\
Score d'attribution de la fraction péréquation de la DSR au titre du nombre d'enfants dans la population"
    reference = ["https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433094&cidTexte=LEGITEXT000006070633",
            "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"]
    documentation = """3° Pour 30 % de son montant, proportionnellement au nombre
    d'enfants de trois à seize ans domiciliés dans la commune, établi lors du dernier
    recensement.
    """

    def formula(commune, period, parameters):
        population_enfants = commune('population_enfants', period)
        dsr_eligible_fraction_perequation = commune("dsr_eligible_fraction_perequation", period)

        return dsr_eligible_fraction_perequation * population_enfants


class dsr_score_attribution_perequation_part_potentiel_financier_par_hectare(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Score DSR fraction péréquation - potentiel financier par hectare:\
Score d'attribution de la fraction péréquation de la DSR au titre du potentiel financier par hectare"
    reference = ["https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433094&cidTexte=LEGITEXT000006070633",
            "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"]
    documentation = """4° Pour 10 % de son montant au maximum, en fonction de
    l'écart entre le potentiel financier par hectare de la commune et le potentiel
    financier moyen par hectare des communes de moins de 10 000 habitants."""

    def formula(commune, period, parameters):
        potentiel_financier = commune('potentiel_financier', period)
        outre_mer = commune('outre_mer', period)
        potentiel_financier_par_habitant = commune('potentiel_financier_par_hectare', period)
        dsr_eligible_fraction_perequation = commune("dsr_eligible_fraction_perequation", period)
        population_dgf = commune('population_dgf', period)
        # oui le taille_max_commune est le même que pour le seuil d'éligibilité, notre paramétrisation est ainsi
        taille_max_commune = parameters(period).dotation_solidarite_rurale.seuil_nombre_habitants
        superficie = commune('superficie', period)
        communes_moins_10000 = (~outre_mer) * (population_dgf < taille_max_commune)

        pot_fin_par_hectare_10000 = (np.sum(communes_moins_10000 * potentiel_financier)
                / np.sum(communes_moins_10000 * superficie))

        facteur_pot_fin = 2 - potentiel_financier_par_habitant / pot_fin_par_hectare_10000

        return dsr_eligible_fraction_perequation * population_dgf * facteur_pot_fin
class dsr_fraction_perequation(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
