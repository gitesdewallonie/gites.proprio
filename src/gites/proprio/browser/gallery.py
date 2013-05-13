# encoding: utf-8
"""
gites.proprio

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

import simplejson
from datetime import datetime
from embedly import Embedly
import zope.interface
from zope.component import getUtility
from five import grok
from z3c.sqlalchemy import getSAWrapper
from Products.CMFCore.utils import getToolByName
from plone.memoize import forever

from affinitic.pwmanager.interfaces import IPasswordManager

from gites.proprio import interfaces


@forever.memoize
def getInformationsForVideo(videoUrl):
    pwManager = getUtility(IPasswordManager, 'embedly')
    key = pwManager.username
    client = Embedly(key)
    embed = client.oembed(videoUrl)
    if embed.error:
        return None
    return {'title': embed.title,
            'thumb': embed.thumbnail_url}


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

    def getVignettes(self, hebPk):
        vignettes = []
        hebergement = self.getHebergementByHebPk(hebPk)
        codeGDW = hebergement.heb_code_gdw
        listeImage = self.context.photos_heb.fileIds()
        for i in range(15):
            photo = "%s%02d.jpg" % (codeGDW, i)
            if photo in listeImage:
                vignettes.append(photo)
        return vignettes

    def getNextVignette(self, hebPk):
        vignettes = []
        hebergement = self.getHebergementByHebPk(hebPk)
        codeGDW = hebergement.heb_code_gdw
        listeImage = self.context.photos_heb.fileIds()
        for i in range(15):
            photo = "%s%02d.jpg" % (codeGDW, i)
            if photo in listeImage:
                vignettes.append(photo)
        if not vignettes:
            return "%s00.jpg" % codeGDW
        else:
            return vignettes[-1]


class GalleryInfo(grok.View, HebergementMixin):
    grok.context(zope.interface.Interface)
    grok.name(u'gallery-info')
    grok.require('zope2.Public')
    grok.implements(interfaces.IGalleryInfo)

    def getHebergementVideo(self, hebPk):
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        hebVideoTable = wrapper.getMapper('hebergement_video')
        query = session.query(hebVideoTable)
        query = query.filter(hebVideoTable.heb_vid_heb_fk == hebPk)
        videoInfos = query.first()
        return videoInfos

    def getInformationsForVideo(self, videoUrl):
        return getInformationsForVideo(videoUrl)

    def updateGallery(self):
        pwManager = getUtility(IPasswordManager, 'embedly')
        key = pwManager.username

        proprio = self.getProprioByLogin()
        proPk = proprio.pro_pk
        request = self.request
        fields = getattr(request, 'form', None)
        if fields is None or fields.get('video_url', None) is None:
            return {'status': None}

        hebPk = int(fields.get('hebPk'))
        if not hebPk in self.getHebergementPksByProprietaire(proPk):
            return {'status': None}

        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        hebVideoTable = wrapper.getMapper('hebergement_video')
        videoUrl = fields.get('video_url')

        if videoUrl == '':
            query = session.query(hebVideoTable)
            query = query.filter(hebVideoTable.heb_vid_heb_fk == hebPk)
            videoInfos = query.first()
            if videoInfos:
                session.delete(videoInfos)
                session.flush()
            return {'status': 1}

        videoUrl = videoUrl.replace("https", "http")
        videoUrl = videoUrl.strip()
        client = Embedly(key)
        if not client.is_supported(videoUrl):
            return {'status': 0}

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


class GalleryUpload(grok.View, HebergementMixin):
    grok.context(zope.interface.Interface)
    grok.name(u'upload-image')
    grok.require('zope2.Public')
    grok.implements(interfaces.IGalleryInfo)

    def render(self):
        pass

    def __call__(self):
        fields = self.request.form
        hebPk = fields.get('hebPk')
        fileUpload = fields.get('file')
        lastImageName = self.getNextVignette(hebPk)
        self.request.response.setHeader('content-type', 'text/x-json')
        self.request.response.setHeader('Cache-Control', 'no-cache')
        return simplejson.dumps({'hebPk': hebPk,
                                 'filename': fileUpload.filename,
                                 'imageName': lastImageName})


class GalleryCrop(grok.View, HebergementMixin):
    grok.context(zope.interface.Interface)
    grok.name(u'crop-image')
    grok.require('zope2.Public')
    grok.implements(interfaces.IGalleryInfo)
