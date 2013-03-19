# encoding: utf-8
"""
gites.proprio

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

import zope.interface
from five import grok
from z3c.sqlalchemy import getSAWrapper

from gites.core.mailer import Mailer

from gites.proprio import interfaces


class HebergementMixin(object):

    def getHebergementByProprietaire(self, proprioFk):
        """
        Sélectionne les infos de l'hébergement d'un proprio selon sa clé
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        hebergementTable = wrapper.getMapper('hebergement')
        query = session.query(hebergementTable)
        query = query.filter(hebergementTable.heb_pro_fk == proprioFk)
        hebergement = query.all()
        return hebergement

    def getHebergementByHebPk(self, hebPk):
        """ Sélectionne les infos d'un proprio selon son login """
        hebPk=int(hebPk)
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        hebergementTable = wrapper.getMapper('hebergement')
        query = session.query(hebergementTable)
        query = query.filter(hebergementTable.heb_pk == hebPk)
        hebergement = query.all()
        return hebergement

    def getHebergementMajByhebPk(self, hebPk):
        """
        Retourne si des infos de maj existe déjà pour un hebergement
        selon sa clé depuis la table hebergement_maj
        """
        hebergementMajExist = False
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        hebergementMajTable = wrapper.getMapper('hebergement_maj')
        query = session.query(hebergementMajTable)
        query = query.filter(hebergementMajTable.heb_maj_hebpk == hebPk)
        records = query.all()
        if len(records) > 0:
            hebergementMajExist = True
        else:
            hebergementMajExist = False
        return hebergementMajExist

    def getTableHote(self):
        """ Sélectionne toutes les table d'hôte """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        tableHoteTable = wrapper.getMapper('table_hote')
        query = session.query(tableHoteTable)
        tableHote = query.all()
        return tableHote

    def getTypeTableHoteByHebPk(self, hebPk):
        """
        retourne les type de table d'hote d'un hebergement
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        typeTableHoteTable = wrapper.getMapper('heb_tab_hote')
        query = session.query(typeTableHoteTable)
        query = query.filter(typeTableHoteTable.hebhot_heb_fk == hebPk)
        records = query.all()
        typeTableHoteForHeb=[]
        for table in records:
            typeTableHoteForHeb.append(table.hebhot_tabho_fk)
        return typeTableHoteForHeb

    def getAllCharge(self):
        """
        Sélectionne les type de charge
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        chargeTable = wrapper.getMapper('charge')
        query = session.query(chargeTable)
        charges = query.all()
        return charges

    def sendMail(self, sujet, message):
        """
        envoi de mail à secretariat GDW
        """
        mailer = Mailer("localhost", "info@gitesdewallonie.be")
        #mailer = Mailer("relay.skynet.be", "alain.meurant@affinitic.be")
        mailer.setSubject(sujet)
        mailer.setRecipients("info@gitesdewallonie.be")
        mail = message
        mailer.sendAllMail(mail)

    def modifyStatutMajHebergement(self, hebPk, hebMajInfoEtat):
        """
        change le statut de mise à jour d'un hebergement
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        updateHebergement = wrapper.getMapper('hebergement')
        query = session.query(updateHebergement)
        query = query.filter(updateHebergement.heb_pk == hebPk)
        records = query.all()
        for record in records:
            record.heb_maj_info_etat = hebMajInfoEtat
        session.flush()

    def insertTypeTableHoteOfHebergementMaj(self, hebPk, tableHotePk):
        """
        ajoute les infos de mise à jour des tables d'hote d'un hebergement
        par le proprio
        table heb_tab_hote_maj
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        insertTypeTableHoteOfHebergementMaj = wrapper.getMapper('heb_tab_hote_maj')
        for table in tableHotePk:
            newEntry = insertTypeTableHoteOfHebergementMaj(hebhot_maj_heb_fk = hebPk,\
                                                           hebhot_maj_tabho_fk = table)
            session.save(newEntry)
        session.flush()

    def deleteTypeTableHoteOfHebergementMajByHebPk(self, hebPk):
        """
        supprime les infos de mise à jour des tables d'hote d'un hebergement
        selon la pk de l'heb
        table heb_tab_hote_maj
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        deleteTypeTableHoteOfHebergementMaj = wrapper.getMapper('heb_tab_hote_maj')
        query = session.query(deleteTypeTableHoteOfHebergementMaj)
        query = query.filter(deleteTypeTableHoteOfHebergementMaj.hebhot_maj_heb_fk == hebPk)
        for table in query.all():
            session.delete(table)
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
        chargeFk=fields.get('heb_maj_charge_fk')
        hebPk=fields.get('heb_maj_hebpk')
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        insertHebergementMaj = wrapper.getMapper('hebergement_maj')
        newEntry = insertHebergementMaj(heb_maj_hebpk=hebPk,\
                                        heb_maj_nom=fields.get('heb_maj_nom'),\
                                        heb_maj_adresse=fields.get('heb_maj_adresse'),\
                                        heb_maj_localite=fields.get('heb_maj_localite'),\
                                        heb_maj_tenis=fields.get('heb_maj_tenis'),\
                                        heb_maj_nautisme=fields.get('heb_maj_nautisme'),\
                                        heb_maj_sky=fields.get('heb_maj_sky'),\
                                        heb_maj_rando=fields.get('heb_maj_rando'),\
                                        heb_maj_piscine=fields.get('heb_maj_piscine'),\
                                        heb_maj_peche=fields.get('heb_maj_peche'),\
                                        heb_maj_equitation=fields.get('heb_maj_equitation'),\
                                        heb_maj_velo=fields.get('heb_maj_velo'),\
                                        heb_maj_vtt=fields.get('heb_maj_vtt'),\
                                        heb_maj_ravel=fields.get('heb_maj_ravel'),\
                                        heb_maj_tarif_we_bs=fields.get('heb_maj_tarif_we_bs'),\
                                        heb_maj_tarif_we_ms=fields.get('heb_maj_tarif_we_ms'),\
                                        heb_maj_tarif_we_hs=fields.get('heb_maj_tarif_we_hs'),\
                                        heb_maj_tarif_sem_bs=fields.get('heb_maj_tarif_sem_bs'),\
                                        heb_maj_tarif_sem_ms=fields.get('heb_maj_tarif_sem_ms'),\
                                        heb_maj_tarif_sem_hs=fields.get('heb_maj_tarif_sem_hs'),\
                                        heb_maj_tarif_garantie=fields.get('heb_maj_tarif_garantie'),\
                                        heb_maj_tarif_divers=fields.get('heb_maj_tarif_divers'),\
                                        heb_maj_descriptif_fr=fields.get('heb_maj_descriptif_fr'),\
                                        heb_maj_pointfort_fr=fields.get('heb_maj_pointfort_fr'),\
                                        heb_maj_fumeur=fields.get('heb_maj_fumeur', 'non'),\
                                        heb_maj_animal=fields.get('heb_maj_animal', 'non'),\
                                        heb_maj_tenis_distance=fields.get('heb_maj_tenis_distance'),\
                                        heb_maj_nautisme_distance=fields.get('heb_maj_nautisme_distance'),\
                                        heb_maj_sky_distance=fields.get('heb_maj_sky_distance'),\
                                        heb_maj_rando_distance=fields.get('heb_maj_rando_distance'),\
                                        heb_maj_piscine_distance=fields.get('heb_maj_piscine_distance'),\
                                        heb_maj_peche_distance=fields.get('heb_maj_peche_distance'),\
                                        heb_maj_equitation_distance=fields.get('heb_maj_equitation_distance'),\
                                        heb_maj_velo_distance=fields.get('heb_maj_velo_distance'),\
                                        heb_maj_vtt_distance=fields.get('heb_maj_vtt_distance'),\
                                        heb_maj_ravel_distance=fields.get('heb_maj_ravel_distance'),\
                                        heb_maj_confort_tv=fields.get('heb_maj_confort_tv'),\
                                        heb_maj_confort_feu_ouvert=fields.get('heb_maj_confort_feu_ouvert'),\
                                        heb_maj_confort_lave_vaiselle=fields.get('heb_maj_confort_lave_vaiselle'),\
                                        heb_maj_confort_micro_onde=fields.get('heb_maj_confort_micro_onde'),\
                                        heb_maj_confort_lave_linge=fields.get('heb_maj_confort_lave_linge'),\
                                        heb_maj_confort_seche_linge=fields.get('heb_maj_confort_seche_linge'),\
                                        heb_maj_confort_congelateur=fields.get('heb_maj_confort_congelateur'),\
                                        heb_maj_confort_internet=fields.get('heb_maj_confort_internet'),\
                                        heb_maj_taxe_sejour=fields.get('heb_maj_taxe_sejour'),\
                                        heb_maj_taxe_montant=fields.get('heb_maj_taxe_montant'),\
                                        heb_maj_forfait_montant=fields.get('heb_maj_forfait_montant'),\
                                        heb_maj_tarif_we_3n=fields.get('heb_maj_tarif_we_3n'),\
                                        heb_maj_tarif_we_4n=fields.get('heb_maj_tarif_we_4n'),\
                                        heb_maj_tarif_semaine_fin_annee=fields.get('heb_maj_tarif_semaine_fin_annee'),\
                                        heb_maj_lit_1p=fields.get('heb_maj_lit_1p'),\
                                        heb_maj_lit_2p=fields.get('heb_maj_lit_2p'),\
                                        heb_maj_lit_sup=fields.get('heb_maj_lit_sup'),\
                                        heb_maj_lit_enf=fields.get('heb_maj_lit_enf'),\
                                        heb_maj_distribution_fr=fields.get('heb_maj_distribution_fr'),\
                                        heb_maj_commerce=fields.get('heb_maj_commerce'),\
                                        heb_maj_restaurant=fields.get('heb_maj_restaurant'),\
                                        heb_maj_gare=fields.get('heb_maj_gare'),\
                                        heb_maj_gare_distance=fields.get('heb_maj_gare_distance'),\
                                        heb_maj_restaurant_distance=fields.get('heb_maj_restaurant_distance'),\
                                        heb_maj_commerce_distance=fields.get('heb_maj_commerce_distance'),\
                                        heb_maj_tarif_chmbr_avec_dej_1p=fields.get('heb_maj_tarif_chmbr_avec_dej_1p'),\
                                        heb_maj_tarif_chmbr_avec_dej_2p=fields.get('heb_maj_tarif_chmbr_avec_dej_2p'),\
                                        heb_maj_tarif_chmbr_avec_dej_3p=fields.get('heb_maj_tarif_chmbr_avec_dej_3p'),\
                                        heb_maj_tarif_chmbr_sans_dej_1p=fields.get('heb_maj_tarif_chmbr_sans_dej_1p'),\
                                        heb_maj_tarif_chmbr_sans_dej_2p=fields.get('heb_maj_tarif_chmbr_sans_dej_2p'),\
                                        heb_maj_tarif_chmbr_sans_dej_3p=fields.get('heb_maj_tarif_chmbr_sans_dej_3p'),\
                                        heb_maj_tarif_chmbr_table_hote_1p=fields.get('heb_maj_tarif_chmbr_table_hote_1p'),\
                                        heb_maj_tarif_chmbr_table_hote_2p=fields.get('heb_maj_tarif_chmbr_table_hote_2p'),\
                                        heb_maj_tarif_chmbr_table_hote_3p=fields.get('heb_maj_tarif_chmbr_table_hote_3p'),\
                                        heb_maj_tarif_chmbr_autre_1p=fields.get('heb_maj_tarif_chmbr_autre_1p'),\
                                        heb_maj_tarif_chmbr_autre_2p=fields.get('heb_maj_tarif_chmbr_autre_2p'),\
                                        heb_maj_tarif_chmbr_autre_3p=fields.get('heb_maj_tarif_chmbr_autre_3p'),\
                                        heb_maj_charge_fk=chargeFk)
        session.save(newEntry)
        session.flush()

    def addHebergementMaj(self):
        """
        gestion de l'ajout des données de maj d'une hebergement
        """
        fields = self.request
        hebPk = fields.get('heb_maj_hebpk')
        hebNom = fields.get('heb_maj_nom')
        tableHotePk=fields.get('hebhot_tabhot_fk', None)

        hebergement = self.getHebergementByHebPk(hebPk)
        for elem in hebergement:
            hebergementPk = elem.heb_pk

        if int(hebPk) == hebergementPk:
            isHebergementMajExist = self.getHebergementMajByhebPk(hebPk)

            if isHebergementMajExist:
                #si une maj existe déjà,
                #    suppression de ce record dans table hebergement_maj
                #    suppression des record table hote
                #    insertion des nouvelles données.
                self.deleteHebergementMajByHebPk(hebPk)
                self.deleteTypeTableHoteOfHebergementMajByHebPk(hebPk)
                self.insertHebergementMaj()
                if tableHotePk:
                    self.insertTypeTableHoteOfHebergementMaj(hebPk, tableHotePk)
            else:
                self.insertHebergementMaj()
                if tableHotePk:
                    self.insertTypeTableHoteOfHebergementMaj(hebPk, tableHotePk)

            hebMajInfoEtat="En attente confirmation"
            self.modifyStatutMajHebergement(hebPk, hebMajInfoEtat)

            sujet="Un proprio a modifie les infos de son hebergement"
            message="""L'hébergement %s dont la référence est %s vient d'être modifié.
                       Il faut vérifer ces données et les valider via le lien"""%(hebNom, hebPk)
            self.sendMail(sujet, message)
            return {'status': 1}
        else:
            sujet="Alerte :: Modification hebergement"
            message="""L'hébergement %s dont la référence est %s n'a pas été modifié.
                       Problème de PK"""%(hebNom, hebPk)
            self.sendMail(sujet, message)
            return {'status': -1}


class HebergementInfo(grok.View, HebergementMixin):
    grok.context(zope.interface.Interface)
    grok.name(u'hebergement-info')
    grok.require('zope2.Public')
    grok.implements(interfaces.IHebergementInfo)


class HebergementUpdate(grok.View, HebergementMixin):
    grok.context(zope.interface.Interface)
    grok.name(u'maj-hebergement-insertion')
    grok.require('zope2.Public')
    grok.implements(interfaces.IHebergementInfo)
