# encoding: utf-8
"""
gites.proprio

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from zope.interface import implements
from Products.Five import BrowserView
from sqlalchemy import and_
from z3c.sqlalchemy import getSAWrapper
from gites.core.mailer import Mailer
from gites.db import content as mappers, \
                     session as Session
from Products.CMFCore.utils import getToolByName
from gites.proprio import interfaces


class ManageCertificatPeb(BrowserView):

    def getCertificatPebByHebPk(self, hebPk):
        """
        Retourne les type de table d'hote d'un hebergement
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        tableHebergement = wrapper.getMapper('hebergement')
        query = session.query(tableHebergement)
        query = query.filter(tableHebergement.heb_pk == hebPk)
        hebergement = query.one()
        return hebergement


    def updateHebergementCertificatPeb(self):
        """
        modifier les données PEB pour un hébergement
        table hebergement
        """

        fields = self.context.REQUEST
        hebPk = getattr(fields, 'hebPk', None)
        hebPebCode = getattr(fields, 'hebPebCode', None)
        hebPebEnergiePrimaire = getattr(fields, 'hebPebEnergiePrimaire', None)
        hebPebEnergieTotale = getattr(fields, 'hebPebEnergieTotale', None)
        hebPebIcone = getattr(fields, 'hebPebIcone', None)

        #insertHebergementMaj = wrapper.getMapper('hebergement_maj')

        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        #query = session.query(Hebergement)
        updateHebergement = wrapper.getMapper('hebergement')
        query = session.query(updateHebergement)
        query = query.filter(updateHebergement.heb_pk == hebPk)
        hebergement = query.one()
        hebergement.heb_peb_code = unicode(hebPebCode, 'utf-8')
        hebergement.heb_peb_energie_primaire = unicode(hebPebEnergiePrimaire, 'utf-8')
        hebergement.heb_peb_energie_totale = unicode(hebPebEnergieTotale, 'utf-8')
        hebergement.heb_peb_icone = unicode(hebPebIcone, 'utf-8')

        session.flush()

        portalUrl = getToolByName(self.context, 'portal_url')()
        ploneUtils = getToolByName(self.context, 'plone_utils')
        message = u"Les données du certificat PEB sont enregistrées !"
        ploneUtils.addPortalMessage(message, 'info')

        #sujet = u"Un proprio a modifie les infos de son hebergement"
        #message = u"""Les données du certificat PEB de l'hébergement
        #              dont la référence est %s vient d'être modifié.""" % (hebPk)
        #self.sendMail(sujet, message.encode('latin1'))

        url = "%s/zone-membre/gerer-le-certificat-peb?heb_pk=%s" % (portalUrl, hebPk)
        self.request.response.redirect(url)
        #return {'status': 1}


