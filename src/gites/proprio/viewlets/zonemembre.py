# -*- coding: utf-8 -*-
from five import grok
from zope import interface
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from plone.memoize.instance import memoize
from z3c.sqlalchemy import getSAWrapper
from gites.calendar.vocabulary import getHebergementsForProprio
from Products.CMFCore.utils import getToolByName

grok.templatedir('templates')
grok.context(interface.Interface)


class ZoneMembreViewletManager(grok.ViewletManager):
    grok.name('gites.zonemembre')
    def available(self):
        return "zone-membre" in self.context.getPhysicalPath()

class CalendrierViewlet(grok.Viewlet):
    grok.order(10)

    def isVisible(self):
        return len(self.getGitesForProprio()) > 0

    def hasActiveConfiguration(self):
        """
        Does the proprio activated the calendar ?
        """
        cal = self.request.get('form.widgets.calendarConfig')
        if cal is not None:
            if cal == ['non actif'] or cal == ['bloque']:
                return False
            else:
                return True
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        for heb in getHebergementsForProprio(self.context, session):
            return (heb.heb_calendrier_proprio != 'non actif')

    def isBlocked(self):
        """
        See if proprio calendars are blocked (due to 40 days delay)
        """
        cal = self.request.get('form.widgets.calendarConfig')
        if cal is not None:
            return (cal == ['bloque'])
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        for heb in getHebergementsForProprio(self.context, session):
            if heb.heb_calendrier_proprio == 'bloque':
                return True
        return False

    @memoize
    def getGitesForProprio(self):
        return getUtility(IVocabularyFactory, name='proprio.hebergements')(self.context)

class MajInfosViewlet(grok.Viewlet):
    grok.order(20)

    def isVisible(self):
        return len(self.getGitesForProprio()) > 0

    @memoize
    def getGitesForProprio(self):
        return getUtility(IVocabularyFactory, name='proprio.hebergements')(self.context)


# register all viewlets in this viewlet manager:
grok.viewletmanager(ZoneMembreViewletManager)
