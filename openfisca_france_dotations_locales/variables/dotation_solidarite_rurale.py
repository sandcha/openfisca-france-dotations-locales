from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *


class dotation_solidarite_rurale(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Dotation de solidarité rurale (DSR)"
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"

    def formula(commune, period, parameters):
        return truc


class dsr_fraction_bourg_centre(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR


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
      strate = commune('strate_demographique', period)

      plafond = 2 * (
        + (strate == 1) * 657.114759
        + (strate == 2) * 722.315256
        + (strate == 3) * 785.439563
        + (strate == 4) * 862.218176
        + (strate == 5) * 940.663574
        + (strate == 6) * 1016.450575
        + (strate == 7) * 1073.239296
        + (strate > 7) * 0
        )

      return (population_dgf < seuil_nombre_habitants) * (potentiel_financier_par_habitant <= plafond)


class dsr_fraction_perequation(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
