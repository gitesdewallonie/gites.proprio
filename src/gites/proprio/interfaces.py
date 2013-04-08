# encoding: utf-8
"""
gites.proprio

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

import zope.interface


class IHebergementInfo(zope.interface.Interface):
    """ Mise à jour info hebergement """

    def addHebergementMaj():
        """
        Ajoute les infos mise à jour par de l'hébergement le prorpio dans
        la table provisoire
        """


class IProprioInfo(zope.interface.Interface):
    """ Mise à jour Info Proprio """
