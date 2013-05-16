# encoding: utf-8
"""
gites.proprio

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

import os
import simplejson
from datetime import datetime
from embedly import Embedly
from PIL import Image, ImageFile
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
        for i in range(40):
            photo = "%s%02d.jpg" % (codeGDW, i)
            if photo in listeImage:
                vignettes.append(photo)
        return vignettes

    def compactVignettes(self, hebPk):
        existingVignettes = self.getVignettes(hebPk)
        utool = getToolByName(self.context, 'portal_url')
        portal = utool.getPortalObject()
        photoStorage = getattr(portal, 'photos_heb')
        dirPath = photoStorage.basepath
        index = 0
        for vignette in existingVignettes:
            existingVignetteNumber = vignette[-6:-4]
            if int(existingVignetteNumber) != index:
                newName = "%s%02d.jpg" % (vignette[:-6], index)
                os.rename(os.path.join(dirPath, vignette),
                          os.path.join(dirPath, newName))
            index += 1

    def createVignette(self, hebPk):
        utool = getToolByName(self.context, 'portal_url')
        portal = utool.getPortalObject()
        hebergement = self.getHebergementByHebPk(hebPk)
        codeGDW = hebergement.heb_code_gdw
        firstPhoto = "%s00.jpg" % codeGDW
        vignetteStorage = getattr(portal, 'vignettes_heb')
        photoStorage = getattr(portal, 'photos_heb')
        origin = '%s/%s' % (photoStorage.basepath, firstPhoto)
        destination = '%s/%s' % (vignetteStorage.basepath, firstPhoto)
        img = Image.open(origin)
        img = img.resize((60, 39), Image.ANTIALIAS)
        img.save(destination, "JPEG")


class GalleryInfo(grok.View, HebergementMixin):
    grok.context(zope.interface.Interface)
    grok.name(u'gallery-info')
    grok.require('zope2.Public')
    grok.implements(interfaces.IGalleryInfo)

    def __call__(self):
        fields = self.request.form
        hebPk = fields.get('hebPk')
        if fields.get('images-orders', None) is None:
            self.compactVignettes(hebPk)
            return super(GalleryInfo, self).__call__()
        imagesOrder = fields.get('images-orders').split('|')
        imagesOrder = [img for img in imagesOrder if img]
        hebergement = self.getHebergementByHebPk(hebPk)
        codeGDW = hebergement.heb_code_gdw

        utool = getToolByName(self.context, 'portal_url')
        portal = utool.getPortalObject()
        photoStorage = getattr(portal, 'photos_heb')
        dirPath = photoStorage.basepath
        listeImage = photoStorage.fileIds()
        # we need to re-order image files by renaming them
        for i in range(40):
            photo = "%s%02d.jpg" % (codeGDW, i)
            if photo in listeImage:
                if photo not in imagesOrder:
                    os.unlink(os.path.join(dirPath, photo))
                else:
                    os.rename(os.path.join(dirPath, photo),
                              os.path.join(dirPath, "%s_rn" % photo))
        index = 0
        for image in imagesOrder:
            newName = "%s%02d.jpg" % (codeGDW, index)
            os.rename(os.path.join(dirPath, "%s_rn" % image),
                      os.path.join(dirPath, newName))
            index += 1
        return super(GalleryInfo, self).__call__()

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
        message = ''
        fileUpload = fields.get('file')
        img = Image.open(fileUpload.name)
        width, height = img.size
        if width < 580 or height < 377:
            message = 'Votre image est trop petite : elle doit faire au moins 580px de large et 377px de haut.'
            return simplejson.dumps({'hebPk': hebPk,
                                     'filename': fileUpload.filename,
                                     'message': message,
                                     'status': -1})

        utool = getToolByName(self.context, 'portal_url')
        portal = utool.getPortalObject()
        tmpStorage = getattr(portal, 'photos_heb_tmp')
        destination = '%s/%s.jpg' % (tmpStorage.basepath, hebPk)
        ImageFile.MAXBLOCK = width * height
        img.save(destination, "JPEG")
        self.request.response.setHeader('content-type', 'text/x-json')
        self.request.response.setHeader('Cache-Control', 'no-cache')
        return simplejson.dumps({'hebPk': hebPk,
                                 'filename': fileUpload.filename,
                                 'width': width,
                                 'message': message,
                                 'status': 1})


class GalleryCrop(grok.View, HebergementMixin):
    grok.context(zope.interface.Interface)
    grok.name(u'crop-image')
    grok.require('zope2.Public')
    grok.implements(interfaces.IGalleryInfo)


class GallerySave(grok.View, HebergementMixin):
    grok.context(zope.interface.Interface)
    grok.name(u'save-image')
    grok.require('zope2.Public')
    grok.implements(interfaces.IGalleryInfo)

    def render(self):
        pass

    def __call__(self):
        fields = self.request.form
        hebPk = fields.get('hebPk')
        coordX = int(fields.get('x'))
        if coordX < 0:
            coordX = 0
        coordY = int(fields.get('y'))
        if coordY < 0:
            coordY = 0
        width = int(float(fields.get('w')))
        height = int(float(fields.get('h')))
        scale = fields.get('scale', '')

        hebergement = self.getHebergementByHebPk(hebPk)
        codeGDW = hebergement.heb_code_gdw

        utool = getToolByName(self.context, 'portal_url')
        portal = utool.getPortalObject()
        tmpStorage = getattr(portal, 'photos_heb_tmp')
        origin = '%s/%s.jpg' % (tmpStorage.basepath, hebPk)
        photoStorage = getattr(portal, 'photos_heb')
        destination = '%s/%s39.jpg' % (photoStorage.basepath, codeGDW)
        img = Image.open(origin)

        if scale:
            imgWidth, imgHeight = img.size
            scaling = float(1000) / imgWidth
            coordX = float(coordX) * scaling
            coordY = float(coordY) * scaling
            width = float(width) * scaling
            height = float(height) * scaling
        box = (int(coordX), int(coordY),
               int(coordX + width), int(coordY + height))
        img = img.crop(box)
        img.save(destination, "JPEG")
        img = Image.open(destination)
        img = img.resize((580, 377), Image.ANTIALIAS)
        img.save(destination, "JPEG")
        os.unlink(origin)
        self.compactVignettes(hebPk)
        self.createVignette(hebPk)
        portalUrl = getToolByName(self.context, 'portal_url')()
        self.request.response.redirect("%s/zone-membre/gallery-info?hebPk=%s" % (portalUrl, hebPk))
        return ''
