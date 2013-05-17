# encoding: utf-8
"""
gites.proprio

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
import os
import simplejson
from PIL import Image, ImageFile
import zope.interface
from five import grok
from z3c.sqlalchemy import getSAWrapper
from Products.CMFCore.utils import getToolByName

from gites.core.mailer import Mailer

from gites.proprio import interfaces
from gites.proprio.browser.common import ZoneMembreMixin


class ProprioMixin(object):

    def getAllCommunes(self):
        """
        Sélectionne les communes et les cp
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        communeTable = wrapper.getMapper('commune')
        query = session.query(communeTable)
        communes = query.all()
        return communes

    def getAllCivilites(self):
        """
        Sélectionne les civilites
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        civiliteTable = wrapper.getMapper('civilite')
        query = session.query(civiliteTable)
        civilites = query.all()
        return civilites

    def getProprioMajByProPk(self, proPk):
        """
        retourne un proprio selon sa clé depuis la table proprio_maj
        """
        proprioMajExist = False
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        proprioMajTable = wrapper.getMapper('proprio_maj')
        query = session.query(proprioMajTable)
        query = query.filter(proprioMajTable.pro_maj_propk == proPk)
        records = query.all()
        if len(records) > 0:
            proprioMajExist = True
        else:
            proprioMajExist = False
        return proprioMajExist

    def sendMail(self, sujet, message):
        """
        envoi de mail à secretariat GDW
        """
        mailer = Mailer("localhost", "info@gitesdewallonie.be")
        mailer.setSubject(sujet)
        mailer.setRecipients("info@gitesdewallonie.be")
        mail = message
        mailer.sendAllMail(mail)

    def modifyStatutMajProprio(self, proPk, proMajInfoEtat):
        """
        change le statut de mise à jour d'un hebergement
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        updateProprio = wrapper.getMapper('proprio')
        query = session.query(updateProprio)
        query = query.filter(updateProprio.pro_pk == proPk)
        record = query.one()
        record.pro_maj_info_etat = proMajInfoEtat
        session.flush()

    def updateProprioMaj(self):
        """
        mise à jour des données maj du proprio
        """
        fields = self.request
        proMajProPk = fields.get('pro_maj_propk')
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        updateProprioMaj = wrapper.getMapper('proprio_maj')
        query = session.query(updateProprioMaj)
        query = query.filter(updateProprioMaj.pro_maj_propk == proMajProPk)
        record = query.one()
        record.pro_maj_civ_fk = fields.get('pro_maj_civ_fk')
        record.pro_maj_nom1 = unicode(fields.get('pro_maj_nom1', ''), 'utf-8')
        record.pro_maj_prenom1 = unicode(fields.get('pro_maj_prenom1', ''), 'utf-8')
        record.pro_maj_nom2 = unicode(fields.get('pro_maj_nom2', ''), 'utf-8')
        record.pro_maj_prenom2 = unicode(fields.get('pro_maj_prenom2', ''), 'utf-8')
        record.pro_maj_societe = unicode(fields.get('pro_maj_societe', ''), 'utf-8')
        record.pro_maj_adresse = unicode(fields.get('pro_maj_adresse', ''), 'utf-8')
        record.pro_maj_com_fk = fields.get('pro_maj_com_fk')
        record.pro_maj_email = fields.get('pro_maj_email')
        record.pro_maj_tel_priv = fields.get('pro_maj_tel_priv')
        record.pro_maj_fax_priv = fields.get('pro_maj_fax_priv')
        record.pro_maj_gsm1 = fields.get('pro_maj_gsm1')
        record.pro_maj_url = fields.get('pro_maj_url')
        record.pro_maj_tva = fields.get('pro_maj_tva')
        record.pro_maj_langue = fields.get('pro_maj_langue')
        session.flush()

    def insertProprioMaj(self):
        """
        insère les infos mise à jour par proprio dans table provisoire
        """
        fields = self.request
        proPk = fields.get('pro_maj_propk')
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        insertProprioMaj = wrapper.getMapper('proprio_maj')
        newEntry = insertProprioMaj(pro_maj_propk=proPk,\
                                    pro_maj_civ_fk=fields.get('pro_maj_civ_fk'),\
                                    pro_maj_nom1=fields.get('pro_maj_nom1'),\
                                    pro_maj_prenom1=fields.get('pro_maj_prenom1'),\
                                    pro_maj_nom2=fields.get('pro_maj_nom2'),\
                                    pro_maj_prenom2=fields.get('pro_maj_prenom2'),\
                                    pro_maj_societe=fields.get('pro_maj_societe'),\
                                    pro_maj_adresse=fields.get('pro_maj_adresse'),\
                                    pro_maj_com_fk=fields.get('pro_maj_com_fk'),\
                                    pro_maj_email=fields.get('pro_maj_email'),\
                                    pro_maj_tel_priv=fields.get('pro_maj_tel_priv'),\
                                    pro_maj_fax_priv=fields.get('pro_maj_fax_priv'),\
                                    pro_maj_gsm1=fields.get('pro_maj_gsm1'),\
                                    pro_maj_url=fields.get('pro_maj_url'),\
                                    pro_maj_tva=fields.get('pro_maj_tva'),\
                                    pro_maj_langue=fields.get('pro_maj_langue'),\
                                    )
        session.add(newEntry)
        session.flush()

    def addProprioMaj(self):
        """
        gestion de l'ajout des données de maj par le proprio
        """
        fields = self.request
        proPk = fields.get('pro_maj_propk')
        proNom = fields.get('pro_maj_nom1')
        proprio = self.getProprioByLogin()
        proprioPk = proprio.pro_pk

        if int(proPk) == proprioPk:
            isProprioMajExist = self.getProprioMajByProPk(proPk)

            if isProprioMajExist:
                self.updateProprioMaj()
            else:
                self.insertProprioMaj()

            proMajInfoEtat = "En attente confirmation"
            self.modifyStatutMajProprio(proPk, proMajInfoEtat)

            sujet = "Modification des donnees personnelles par un proprio"
            message = """Le proprio %s dont la référence est %s vient de modifier ses
                         données. Il faut les vérifier et les valider
                         via le lien suivant http://gdwadmin.affinitic.be/""" % (proNom, proPk)
            self.sendMail(sujet, message)
            return {'status': 1}
        else:
            sujet = "Un proprio a essayé modifié ses données personnelles"
            message = """Le proprio %s dont la référence est %s a essayé de modifier ses
                         données. Le processus est avorté suite à un problème de PK""" % (proNom, proPk)
            self.sendMail(sujet, message)
            return {'status': -1}


class ProprioInfo(grok.View, ProprioMixin, ZoneMembreMixin):
    grok.context(zope.interface.Interface)
    grok.name(u'proprio-info')
    grok.require('zope2.Public')
    grok.implements(interfaces.IProprioInfo)

    def getPhotoContact(self, proPk):
        utool = getToolByName(self.context, 'portal_url')
        portal = utool.getPortalObject()
        photoStorage = getattr(portal, 'photos_proprio')
        photoName = "%s.jpg" % proPk
        if photoName in photoStorage.fileIds():
            return photoName
        else:
            return None


class ProprioInfoInsert(grok.View, ProprioMixin, ZoneMembreMixin):
    grok.context(zope.interface.Interface)
    grok.name(u'maj-info_proprio-insertion')
    grok.require('zope2.Public')
    grok.implements(interfaces.IProprioInfo)


class ProprioPhotoUpload(grok.View, ZoneMembreMixin):
    grok.context(zope.interface.Interface)
    grok.name(u'upload-image-proprio')
    grok.require('zope2.Public')
    grok.implements(interfaces.IGalleryInfo)

    def render(self):
        pass

    def __call__(self):
        fields = self.request.form
        proPk = fields.get('proPk')
        message = ''
        fileUpload = fields.get('file')

        extension = fileUpload.filename.split('.')[-1]
        if not extension.lower() in ['jpg', 'jpeg', 'png', 'gif']:
            message = 'Votre image doit être au format JPEG, PNG ou GIF.'
            return simplejson.dumps({'proPk': proPk,
                                     'filename': fileUpload.filename,
                                     'message': message,
                                     'status': -1})

        img = Image.open(fileUpload.name)
        width, height = img.size
        if width < 196 or height < 170:
            message = 'Votre image est trop petite : elle doit faire au moins 196px de large et 170px de haut.'
            return simplejson.dumps({'proPk': proPk,
                                     'filename': fileUpload.filename,
                                     'message': message,
                                     'status': -1})

        utool = getToolByName(self.context, 'portal_url')
        portal = utool.getPortalObject()
        tmpStorage = getattr(portal, 'photos_proprio_tmp')
        destination = '%s/%s.jpg' % (tmpStorage.basepath, proPk)
        ImageFile.MAXBLOCK = width * height
        img.save(destination, "JPEG")
        self.request.response.setHeader('content-type', 'text/x-json')
        self.request.response.setHeader('Cache-Control', 'no-cache')
        return simplejson.dumps({'proPk': proPk,
                                 'filename': fileUpload.filename,
                                 'width': width,
                                 'message': message,
                                 'status': 1})


class ProprioPhotoCrop(grok.View, ZoneMembreMixin):
    grok.context(zope.interface.Interface)
    grok.name(u'crop-image-proprio')
    grok.require('zope2.Public')
    grok.implements(interfaces.IGalleryInfo)


class ProprioPhotoSave(grok.View, ZoneMembreMixin):
    grok.context(zope.interface.Interface)
    grok.name(u'save-image-proprio')
    grok.require('zope2.Public')
    grok.implements(interfaces.IGalleryInfo)

    def render(self):
        pass

    def __call__(self):
        fields = self.request.form
        proPk = fields.get('proPk')
        coordX = int(fields.get('x'))
        if coordX < 0:
            coordX = 0
        coordY = int(fields.get('y'))
        if coordY < 0:
            coordY = 0
        width = int(float(fields.get('w')))
        height = int(float(fields.get('h')))
        scale = fields.get('scale', '')

        utool = getToolByName(self.context, 'portal_url')
        portal = utool.getPortalObject()
        tmpStorage = getattr(portal, 'photos_proprio_tmp')
        origin = '%s/%s.jpg' % (tmpStorage.basepath, proPk)
        photoStorage = getattr(portal, 'photos_proprio')
        destination = '%s/%s.jpg' % (photoStorage.basepath, proPk)
        img = Image.open(origin)

        if scale:
            imgWidth, imgHeight = img.size
            scaling = imgWidth / float(1000)
            coordX = float(coordX) * scaling
            coordY = float(coordY) * scaling
            width = float(width) * scaling
            height = float(height) * scaling
        box = (int(coordX), int(coordY),
               int(coordX + width), int(coordY + height))
        img = img.crop(box)
        img.save(destination, "JPEG")
        img = Image.open(destination)
        img = img.resize((196, 170), Image.ANTIALIAS)
        img.save(destination, "JPEG")
        os.unlink(origin)
        portalUrl = getToolByName(self.context, 'portal_url')()
        self.request.response.redirect("%s/zone-membre/proprio-info" % portalUrl)
        return ''
