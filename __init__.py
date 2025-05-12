# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from . import z_human_ressource

__all__ = ['register']


def register():
    Pool.register(
        z_human_ressource.Demission,
        z_human_ressource.Candidat,
        z_human_ressource.Conges,
        z_human_ressource.Entretien,
        z_human_ressource.EntretienCandidat,
        z_human_ressource.Offres,
        z_human_ressource.Absences,
        module='z_human_ressource', type_='model')
    Pool.register(
        module='z_human_ressource', type_='wizard')
    Pool.register(
        module='z_human_ressource', type_='report')
