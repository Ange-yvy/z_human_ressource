##############################################################################
#
#    GNU Health HMIS: The Free Health and Hospital Information System
#    Copyright (C) 2008-2022 Luis Falcon <falcon@gnuhealth.org>
#    Copyright (C) 2011-2022 GNU Solidario <health@gnusolidario.org>
#    Copyright (C) 2015 Cédric Krier
#    Copyright (C) 2014-2015 Chris Zimmerman <siv@riseup.net>
#
#    The GNU Health HMIS component is part of the GNU Health project
#    www.gnuhealth.org
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from decimal import Decimal
from collections import defaultdict, namedtuple
from itertools import combinations
from datetime import datetime, date

from num2words import num2words
from sql import Null
from sql.aggregate import Sum
from sql.conditionals import Coalesce, Case
from sql.functions import Round
import time
from datetime import datetime
import json
import requests
from trytond.i18n import gettext
from trytond.model import Workflow, ModelView, ModelSQL, fields, \
    sequence_ordered, Unique, DeactivableMixin, dualmethod
from trytond.model.exceptions import AccessError
from trytond.pyson import PYSONEncoder
from trytond.report import Report
from trytond.wizard import Wizard, StateView, StateTransition, StateAction, \
    Button
from trytond import backend
from trytond.pyson import If, Eval, Bool
from trytond.tools import reduce_ids, grouped_slice, firstline
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.rpc import RPC
from trytond.config import config
from num2words import num2words
from trytond.modules.product import round_price

import psycopg2
import string
import random
import requests
import json

from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.modules.account.tax import TaxableMixin
from trytond.modules.product import price_digits
from trytond.modules.health.core import get_health_professional

class Demission(ModelSQL, ModelView):
    'User Demissions'
    __name__ = "res.user.demission"

    date_notification = fields.DateTime("Date de Notification", help="Date à laquelle la demande de démission a été générée.")
    date_depart = fields.DateTime("Date de Départ", help="Date à laquelle l'employé n'est plus admis en entreprise.")
    motif = fields.Char("Motif de Démission", help="Motif de démission.")
    user_id = fields.Many2One('res.user-company.employee', "Employé", help="Utilisateur déposant la démission.")
    validate = fields.Boolean("Validate", help="Validé si la demission est effective.")

class Conges(ModelSQL, ModelView):
    'User - Conges'
    __name__ = "res.user.conges"

    date_demande = fields.DateTime("Date", help="Date de la demande en congé.")
    motif = fields.Char("Motif", help="Motif de la demande de congés.")
    debut = fields.DateTime("Date Début", help="Date de début des congés")
    fin = fields.DateTime("Date Fin", help="Date de Fin des congés.")
    validate_superviseur = fields.Boolean("Validé Par Le Superviseur", help="Vrai si le congé a été validé par le superviseur.")
    validate_HR = fields.Boolean("Validé Par La RH", help="Vrai si le congé a été validé par les RH.")
    user_id = fields.Many2One("res.user-company.employee", "Employé", help="Employé demandant les Congés.")

class Absences(ModelSQL, ModelView):
    "User - Absences"
    __name__ = "res.user.absences"

    date_demande = fields.DateTime("Date", help="Date de la demande des absences.")
    motif = fields.Char("Motif", help="Motif de la demande d'absence.")
    debut = fields.DateTime("Date Début", help="Date de début.")
    fin = fields.DateTime("Date Fin", help="Date de Fin.")
    validate_superviseur = fields.Boolean("Validé Par Le Superviseur", help="Vrai si le congé a été validé par le superviseur.")
    validate_HR = fields.Boolean("Validé Par La RH", help="Vrai si le congé a été validé par les RH.")
    user_id = fields.Many2One("res.user-company.employee", "Employé", help="Employé demandant les Congés.")

class Offres(ModelSQL, ModelView):
    "Compagnies Offres"
    __name__ = "compagny.offres"

    titre = fields.Char("Titre de l'offre", help="")
    description = fields.Text("Description de l'offre", help="La description de l'offre.")
    date_publication = fields.DateTime("Date de publication", help="La date de publication de l'offre.")
    date_fin = fields.DateTime("Date de fin", help="Date Limite de Candidature.")
    compagny = fields.Many2One('company.company', "Compagnie", help="La Compagnie à l'origine de l'offre d'emploie.")

class Entretien(ModelSQL, ModelView):
    "Candidat Entretien"
    __name__ = "candidat.entretien"

    date_entretien = fields.DateTime("Date de l'enntretien", help="Date de l'entretien.")
    note = fields.Char("Remarques-Description", help="Une Note, Une remarque ou description Concerant l'entretien")
    candidats = fields.Many2Many('recrutement.entretien-candidat', 'entretien', 'candidat', 'Candidats')
    offre_id = fields.Many2One("compagny.offres", 'Offre', required=True)

class Candidat(ModelSQL, ModelView):
    "Candidat Class"
    __name__ = "res.user.candidat"

    user_id = fields.Many2One("party.party", "Candidat", help="Le candidat à une offre.")
    date_candidature = fields.DateTime("Date de Candidature", help='Date de Candidature')
    entretiens = fields.Many2Many('recrutement.entretien-candidat', 'candidat', 'entretien', 'Entretiens')
    offre_id = fields.Many2One("compagny.offres", "Offre", help="L'Offre.")
    cv = fields.Binary("Curriculum Vitae", help="Le CV de l'employé ou du candidat.")
    diplome = fields.Binary("Diplôme", help="Le diplome le plus élevé.")
    cni = fields.Binary("CNI", help="Carte Nationale d'Identité.")
    autre = fields.Binary("Autre Documents", help="Le reste des documents en 1 fichier.")

class EntretienCandidat(ModelSQL):
    "Entretien-Classe"
    __name__ = 'recrutement.entretien-candidat'

    entretien = fields.Many2One('candidat.entretien', 'Entretien', required=True, ondelete='CASCADE')
    candidat = fields.Many2One('res.user.candidat', 'Candidat', required=True, ondelete='CASCADE')

class Stagiaires(ModelSQL, ModelView):
    "Class Stagiaire"
    __name__ ="res.user.stagiaire"

    user_id = fields.Many2One('party.party', "Personne", help='La personne Candidat')
    date_debut = fields.Date("Date de Début", help="Date de Début du Stage")
    date_fin = fields.Date("Date de Fin", help="Date de fin de Stage.")
    type_stagiaire = fields.Char('Type du Stage', help="Type du Stage")

    
class Ressource_Humaine(ModelSQL,ModelView):
        "Class Ressource_Humaine"
        _name_= "res.user.ressource_humaine"
        user_id = fields.Many2One('party.party', "Personne", help='ressource_humaine')
        

        

