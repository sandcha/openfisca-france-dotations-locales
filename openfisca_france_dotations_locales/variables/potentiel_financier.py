import numpy as np

from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *


class potentiel_financier(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Potentiel financier de la commune"


class potentiel_financier_par_habitant_moyen(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Potentiel financier par habitant moyen (PFi) des communes appartenant à la même strate"
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"

    def formula(commune, period, parameters):
        potentiel_financier_par_habitant = commune('potentiel_financier_par_habitant', period)
        potentiel_financier = commune('potentiel_financier', period)
        strate_demographique = commune('strate_demographique', period)
        population_dgf = commune('population_dgf', period)
        outre_mer = commune('outre_mer', period)

        liste_strates = np.ndarray(range(1+int(strate_demographique.max())))
        
        potentiel_financier_par_strate = np.fromiter(
            (
                (np.sum((~outre_mer) *(strate == strate_demographique)* potentiel_financier)/
                np.sum((~outre_mer) *(strate == strate_demographique)* population_dgf))
                if np.sum((~outre_mer) *(strate == strate_demographique)* population_dgf) > 0.01
                else 0
                for strate in liste_strates
                ),
            dtype = float
            )
        return potentiel_financier_par_strate[strate_demographique]


class potentiel_financier_par_habitant(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR

    def formula(commune, period, parameters):
        return commune('potentiel_financier', period) / commune('population_dgf', period)
