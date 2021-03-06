# encoding: utf-8
"""
gites.proprio

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

import random
from httplib import HTTPConnection
from urlparse import urlparse
from z3c.sqlalchemy import getSAWrapper
from Products.CMFCore.utils import getToolByName

import logging


class ZoneMembreMixin(object):

    def random(self):
        """
        Generate random number to invalidate browser cache for images
        """
        return random.randrange(1, 1000000)

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
        query = query.filter(proprioTable.pro_etat == True)
        proprio = query.first()
        return proprio

    def purgeCacheForImages(self, imagesUrls):
        if not imagesUrls:
            return
        logger = logging.getLogger('gites.proprio')
        baseUrl = urlparse(imagesUrls[0])
        connection = HTTPConnection(baseUrl.hostname, baseUrl.port or 80)
        purgedImages = []
        for url in imagesUrls:
            if url in purgedImages:
                continue
            purgedImages.append(url)
            url = urlparse(url)
            logger.warning('Purging URL : %s' % url.path)
            connection.request('PURGE', url.path, '', {'Host': url.hostname})
            connection.getresponse().read()
        connection.close()
