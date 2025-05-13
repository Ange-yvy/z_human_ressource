# -*- coding: utf-8 -*-
##############################################################################
#
#    GNU Health: The Free Health and Hospital Information System
#    Copyright (C) 2008-2022 Luis Falcon <lfalcon@gnusolidario.org>
#    Copyright (C) 2011-2022 GNU Solidario <health@gnusolidario.org>
#
#
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
import re
from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateTransition, StateView, Button
from trytond.pool import Pool, Transaction
from datetime import date, datetime, time


class ValidateCandidatInit(ModelView):
    'INIT OF Validate Candidat TO EMPLOYE'
    __name__ = 'validate.candidat.init'

    supervisor = fields.Many2One('company.employee', 'Superviseur', help="Le Superviseur des différents candidats à valider.")


class ValidateCandidat(Wizard):
    'Validate Candidat TO EMPLOYE'
    __name__ = 'validate.candidat'

    start = StateView('validate.candidat.init',
        'z_human_ressource.validate_candidat_init', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Generate Validation', 'generate_validate', 'tryton-ok',
                True),
            ])
    
    generate_validate = StateTransition()
    
    def transition_generate_validate(self):
        Employee = Pool().get("company.employee")
        Candidat = Pool().get("res.user.candidat")

        candidats = Candidat.browse(Transaction().context.get(
            'active_ids'))
        
        list_candidats = []
        for candidat in candidats:
            employee_data = {}
            if candidat.user_id is not None:
                employee_data['party'] = candidat.user_id
                employee_data['supervisor'] = self.start.supervisor
                employee_data['company'] =  Transaction().context.get('company')
                employee_data['start_date'] = datetime.date()

            list_candidats.append(employee_data)
        
        Employee.create(list_candidats)

        return 'end'


        
