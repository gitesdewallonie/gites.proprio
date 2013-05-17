# encoding: utf-8
"""
gites.proprio

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from five import grok
import zope.interface
from z3c.sqlalchemy import getSAWrapper

from gites.core.mailer import Mailer

from gites.proprio.interfaces import IProprioInfo
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
    grok.implements(IProprioInfo)


class ProprioInfoInsert(grok.View, ProprioMixin, ZoneMembreMixin):
    grok.context(zope.interface.Interface)
    grok.name(u'maj-info_proprio-insertion')
    grok.require('zope2.Public')
    grok.implements(IProprioInfo)
