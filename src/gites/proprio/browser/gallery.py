# encoding: utf-8
"""
gites.proprio

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

from datetime import datetime
from embedly import Embedly
import zope.interface
from zope.component import getUtility
from five import grok
from z3c.sqlalchemy import getSAWrapper
from Products.CMFCore.utils import getToolByName

from affinitic.pwmanager.interfaces import IPasswordManager

from gites.proprio import interfaces


class HebergementMixin(object):

    def getHebergementPksByProprietaire(self, proprioPk):
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        hebergementTable = wrapper.getMapper('hebergement')
        query = session.query(hebergementTable)
        query = query.filter(hebergementTable.heb_pro_fk == proprioPk)
        hebergements = query.all()
        return [heb.heb_pk for heb in hebergements]

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

    def getHebergementByHebPk(self, hebPk):
        """ Sélectionne les infos d'un proprio selon son login """
        proprio = self.getProprioByLogin()
        hebPk = int(hebPk)
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        hebergementTable = wrapper.getMapper('hebergement')
        query = session.query(hebergementTable)
        query = query.filter(hebergementTable.heb_pk == hebPk)
        query = query.filter(hebergementTable.heb_pro_fk == proprio.pro_pk)
        hebergement = query.all()
        return hebergement

    def getHebergementVideo(self, hebPk):
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        hebVideoTable = wrapper.getMapper('hebergement_video')
        query = session.query(hebVideoTable)
        query = query.filter(hebVideoTable.heb_vid_heb_fk == hebPk)
        videoInfos = query.first()
        return videoInfos

    def updateGallery(self):
        pwManager = getUtility(IPasswordManager, 'embedly')
        key = pwManager.username

        proprio = self.getProprioByLogin()
        proPk = proprio.pro_pk
        request = self.request
        fields = getattr(request, 'form', None)
        if not fields or not fields.get('video_url', None):
            return {'status': None}

        hebPk = int(fields.get('hebPk'))
        if not hebPk in self.getHebergementPksByProprietaire(proPk):
            return {'status': None}

        videoUrl = fields.get('video_url')
        videoUrl = videoUrl.replace("https", "http")
        videoUrl = videoUrl.strip()
        client = Embedly(key)
        if not client.is_supported(videoUrl):
            return {'status': 0}

        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        hebVideoTable = wrapper.getMapper('hebergement_video')
        query = session.query(hebVideoTable)
        query = query.filter(hebVideoTable.heb_vid_heb_fk == hebPk)
        videoInfos = query.first()
        if not videoInfos:
            videoInfos = hebVideoTable()
        videoInfos.heb_vid_url = videoUrl
        videoInfos.heb_vid_date = datetime.now()
        videoInfos.heb_vid_heb_fk = hebPk
        session.add(videoInfos)
        session.flush()
        return {'status': 1}


class GalleryInfo(grok.View, HebergementMixin):
    grok.context(zope.interface.Interface)
    grok.name(u'gallery-info')
    grok.require('zope2.Public')
    grok.implements(interfaces.IGalleryInfo)
