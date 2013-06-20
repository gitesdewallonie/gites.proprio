# encoding: utf-8
"""
gites.proprio

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

import zope.interface
from five import grok
from sqlalchemy import and_
from z3c.sqlalchemy import getSAWrapper

from gites.core.mailer import Mailer
from gites.db import content as mappers, session as Session

from gites.proprio import interfaces
from gites.proprio.browser.common import ZoneMembreMixin


class HebergementMixin(object):

    def getTableHote(self):
        """ Sélectionne toutes les table d'hôte """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        tableHoteTable = wrapper.getMapper('table_hote')
        query = session.query(tableHoteTable)
        tableHote = query.all()
        return tableHote

    def getTypeTableHoteByHebPk(self, hebPk):
        """ Retourne les type de table d'hote d'un hebergement """
        met_ids = ('heb_tabhot_repas_familial',
                   'heb_tabhot_gastronomique',
                   'heb_tabhot_gourmand')
        session = getSAWrapper('gites_wallons').session
        query = session.query(mappers.Hebergement).join('activeMetadatas')
        query = query.filter(and_(mappers.Hebergement.heb_pk == hebPk,
                                  mappers.Metadata.met_id.in_(met_ids)))
        return query.all()

    def getAllCharge(self):
        """ Sélectionne les type de charge """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        chargeTable = wrapper.getMapper('charge')
        query = session.query(chargeTable)
        charges = query.all()
        return charges

    def sendMail(self, sujet, message):
        """ Envoi de mail à secretariat GDW """
        mailer = Mailer("localhost", "info@gitesdewallonie.be")
        mailer.setSubject(sujet)
        mailer.setRecipients("info@gitesdewallonie.be")
        mail = message
        mailer.sendAllMail(mail)

    def modifyStatutMajHebergement(self, hebPk, hebMajInfoEtat):
        """ Change le statut de mise à jour d'un hebergement """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        updateHebergement = wrapper.getMapper('hebergement')
        query = session.query(updateHebergement)
        query = query.filter(updateHebergement.heb_pk == hebPk)
        records = query.all()
        for record in records:
            record.heb_maj_info_etat = hebMajInfoEtat
        session.flush()

    def deleteHebergementMajByHebPk(self, hebPk):
        """
        supprime les infos de mise à jour d'un hebergement
        selon la pk de l'heb
        table hebebergement_maj
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        deleteHebergementMaj = wrapper.getMapper('hebergement_maj')
        query = session.query(deleteHebergementMaj)
        query = query.filter(deleteHebergementMaj.heb_maj_hebpk == hebPk)
        for table in query.all():
            session.delete(table)
        session.flush()

    def insertHebergementMaj(self):
        """
        ajoute les infos de mise à jour de l'hébergement par le proprio
        table habergement_maj
        met dans table hebergement le champ heb_maj_info_etat à 'En attente de confirmation'
        """
        fields = self.context.REQUEST
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        insertHebergementMaj = wrapper.getMapper('hebergement_maj')
        newEntry = insertHebergementMaj(
            heb_maj_hebpk=fields.get('heb_maj_hebpk'),
            heb_maj_nom=fields.get('heb_maj_nom'),
            heb_maj_adresse=fields.get('heb_maj_adresse'),
            heb_maj_localite=fields.get('heb_maj_localite'),
            heb_maj_tarif_we_bs=fields.get('heb_maj_tarif_we_bs'),
            heb_maj_tarif_we_ms=fields.get('heb_maj_tarif_we_ms'),
            heb_maj_tarif_we_hs=fields.get('heb_maj_tarif_we_hs'),
            heb_maj_tarif_sem_bs=fields.get('heb_maj_tarif_sem_bs'),
            heb_maj_tarif_sem_ms=fields.get('heb_maj_tarif_sem_ms'),
            heb_maj_tarif_sem_hs=fields.get('heb_maj_tarif_sem_hs'),
            heb_maj_tarif_garantie=fields.get('heb_maj_tarif_garantie'),
            heb_maj_tarif_divers=fields.get('heb_maj_tarif_divers'),
            heb_maj_descriptif_fr=fields.get('heb_maj_descriptif_fr'),
            heb_maj_pointfort_fr=fields.get('heb_maj_pointfort_fr'),
            heb_maj_taxe_montant=fields.get('heb_maj_taxe_montant'),
            heb_maj_forfait_montant=fields.get('heb_maj_forfait_montant'),
            heb_maj_tarif_we_3n=fields.get('heb_maj_tarif_we_3n'),
            heb_maj_tarif_we_4n=fields.get('heb_maj_tarif_we_4n'),
            heb_maj_tarif_semaine_fin_annee=fields.get('heb_maj_tarif_semaine_fin_annee'),
            heb_maj_lit_1p=fields.get('heb_maj_lit_1p'),
            heb_maj_lit_2p=fields.get('heb_maj_lit_2p'),
            heb_maj_lit_sup=fields.get('heb_maj_lit_sup'),
            heb_maj_lit_enf=fields.get('heb_maj_lit_enf'),
            heb_maj_distribution_fr=fields.get('heb_maj_distribution_fr'),
            heb_maj_tarif_chmbr_avec_dej_1p=fields.get('heb_maj_tarif_chmbr_avec_dej_1p'),
            heb_maj_tarif_chmbr_avec_dej_2p=fields.get('heb_maj_tarif_chmbr_avec_dej_2p'),
            heb_maj_tarif_chmbr_avec_dej_3p=fields.get('heb_maj_tarif_chmbr_avec_dej_3p'),
            heb_maj_tarif_chmbr_sans_dej_1p=fields.get('heb_maj_tarif_chmbr_sans_dej_1p'),
            heb_maj_tarif_chmbr_sans_dej_2p=fields.get('heb_maj_tarif_chmbr_sans_dej_2p'),
            heb_maj_tarif_chmbr_sans_dej_3p=fields.get('heb_maj_tarif_chmbr_sans_dej_3p'),
            heb_maj_tarif_chmbr_table_hote_1p=fields.get('heb_maj_tarif_chmbr_table_hote_1p'),
            heb_maj_tarif_chmbr_table_hote_2p=fields.get('heb_maj_tarif_chmbr_table_hote_2p'),
            heb_maj_tarif_chmbr_table_hote_3p=fields.get('heb_maj_tarif_chmbr_table_hote_3p'),
            heb_maj_tarif_chmbr_autre_1p=fields.get('heb_maj_tarif_chmbr_autre_1p'),
            heb_maj_tarif_chmbr_autre_2p=fields.get('heb_maj_tarif_chmbr_autre_2p'),
            heb_maj_tarif_chmbr_autre_3p=fields.get('heb_maj_tarif_chmbr_autre_3p'),
            heb_maj_charge_fk=fields.get('heb_maj_charge_fk'))
        session.add(newEntry)
        session.flush()

    def addHebergementMaj(self):
        """ Gestion de l'ajout des données de maj d'une hebergement """
        fields = self.request
        hebPk = fields.get('heb_maj_hebpk')
        hebNom = fields.get('heb_maj_nom')

        hebergement = self.getHebergementByHebPk(hebPk)
        hebergementPk = hebergement.heb_pk

        if int(hebPk) == hebergementPk:
            # Verifies if there's updates awaiting of validation
            # If this is the case we delete the records
            if mappers.HebergementMaj.exists(heb_maj_hebpk=hebPk) is True:
                self.deleteHebergementMajByHebPk(hebPk)
                self.delete_metadata_updates(hebPk)
                self.insertHebergementMaj()
                self.insert_metadata_updates(hebPk)
            else:
                self.insertHebergementMaj()
                self.insert_metadata_updates(hebPk)

            hebMajInfoEtat = "En attente confirmation"
            self.modifyStatutMajHebergement(hebPk, hebMajInfoEtat)

            sujet = u"Un proprio a modifie les infos de son hebergement"
            message = u"""
                L'hébergement %s dont la référence est %s vient d'être modifié.
                Il faut vérifer ces données et les valider via le lien""" % (hebNom, hebPk)
            self.sendMail(sujet, message)
            return {'status': 1}
        else:
            sujet = u"Alerte :: Modification hebergement"
            message = u"""L'hébergement %s dont la référence est %s n'a pas été modifié.
                       Problème de PK""" % (hebNom, hebPk)
            self.sendMail(sujet, message)
            return {'status': -1}

    def insert_missing_metadata(self, heb_pk):
        """ Adds record for the new metadatas that can be edited """
        editable = mappers.Metadata.get_editable()
        current = self.get_editable_metadata()
        for metadata in [e for e in editable if e.met_pk not in [c.pk for c \
                                                                 in current]]:
            link = mappers.LinkHebergementMetadata(
                heb_fk=heb_pk,
                metadata_fk=metadata.met_pk,
                link_met_value=False)
            link.insert()

    def delete_metadata_updates(self, heb_pk):
        """
        Deletes all the records in the link_hebergement_metadata_update for
        the given hebergement pk
        """
        session = Session()
        query = session.query(mappers.LinkHebergementMetadataUpdate).join(
            'link_metadata')
        query = query.filter(mappers.LinkHebergementMetadata.heb_fk == heb_pk)
        for metadata in query.all():
            session.delete(metadata)

    def insert_metadata_updates(self, heb_pk):
        """ Inserts the updates for the metadatas """
        metadata_list = self.get_metadata(heb_pk, editable=True)
        for current_metadata in metadata_list:
            metadata_id = str(current_metadata.metadata_fk)
            value = bool(self.request.get(metadata_id) or False)
            if value != current_metadata.link_met_value:
                update = mappers.LinkHebergementMetadataUpdate(
                    link_met_fk=current_metadata.link_met_pk,
                    metadata_fk=current_metadata.metadata_fk,
                    link_met_value=value)
                update.insert()

    def get_editable_metadata(self, metadata_type=None):
        """ Returns all the metadata object for editing """
        return mappers.LinkHebergementMetadata.get_metadata(
            self.request.get('hebPk'),
            self.request.get('LANGUAGE', 'fr'),
            editable=True,
            type=metadata_type)

    def get_metadata(self, heb_pk, editable=None):
        """ Returns all the metadata for the given heb pk """
        session = getSAWrapper('gites_wallons').session
        query = session.query(mappers.LinkHebergementMetadata)
        query = query.join('metadata_info')
        query = query.filter(mappers.LinkHebergementMetadata.heb_fk == heb_pk)
        if editable is not None:
            query = query.filter(mappers.Metadata.met_editable == editable)
        return query.all()


class HebergementInfo(grok.View, HebergementMixin, ZoneMembreMixin):
    grok.context(zope.interface.Interface)
    grok.name(u'hebergement-info')
    grok.require('zope2.Public')
    grok.implements(interfaces.IHebergementInfo)

    def update(self):
        self.insert_missing_metadata(self.request.get('hebPk'))


class HebergementUpdate(grok.View, HebergementMixin, ZoneMembreMixin):
    grok.context(zope.interface.Interface)
    grok.name(u'maj-hebergement-insertion')
    grok.require('zope2.Public')
    grok.implements(interfaces.IHebergementInfo)
