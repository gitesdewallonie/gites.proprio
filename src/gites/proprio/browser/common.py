# encoding: utf-8
"""
gites.proprio

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

from z3c.sqlalchemy import getSAWrapper
from Products.CMFCore.utils import getToolByName


class ZoneMembreMixin(object):

    def getHebergementByHebPk(self, hebPk):
        proprio = self.getProprioByLogin()
        hebPk = int(hebPk)
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        hebergementTable = wrapper.getMapper('hebergement')
        query = session.query(hebergementTable)
        query = query.filter(hebergementTable.heb_pk == hebPk)
        query = query.filter(hebergementTable.heb_pro_fk == proprio.pro_pk)
        hebergement = query.first()
        return hebergement

    def getProprioByLogin(self):
        """
        Sélectionne les infos d'un proprio selon son login
        """
        pm = getToolByName(self, 'portal_membership')
        user = pm.getAuthenticatedMember()
        proprioLogin = user.getUserName()
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        proprioTable = wrapper.getMapper('proprio')
        query = session.query(proprioTable)
        query = query.filter(proprioTable.pro_log == proprioLogin)
        proprio = query.first()
        return proprio
