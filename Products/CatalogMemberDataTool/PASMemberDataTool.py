"""
Catalog MemberData Tool

Author: Brent Hendricks
(C) 2005 Rice University

This software is subject to the provisions of the GNU General
Public License Version 2 (GPL).  See LICENSE.txt for details.

This file contains code derived from CMFCore.MemberDataTool and
CMFPlone.MemberDataTool
"""

"""
$Id: MemberDataTool.py,v 1.1 2005/05/31 17:23:11 brentmh Exp $
"""

import AccessControl
from Globals import InitializeClass
from Acquisition import aq_base, aq_parent, aq_inner
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.permissions import ManagePortal, ViewManagementScreens

# We'll use Plone's MemberData if it's present
try:
    from Products.PlonePAS.tools.memberdata import MemberData as BaseMemberData
except ImportError:
    try:
        from Products.CMFPlone.MemberDataTool import MemberData as BaseMemberData
    except ImportError:
        from Products.CMFCore.MemberDataTool import MemberData as BaseMemberData

from Products.CMFCore.interfaces.portal_memberdata import portal_memberdata as IMemberDataTool
from Products.CMFCore.interfaces.portal_memberdata import MemberData as IMemberData

MEMBER_CATALOG = 'member_catalog'


def addMemberDataTool(self,REQUEST=None):
    ''' '''
    mt=MemberDataTool()
    self._setObject('portal_memberdata',mt,set_owner=0)
    if REQUEST:
        return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

class MemberDataTool(UniqueObject, BTreeFolder2):
    """Stores MemberData objects in a folder so they can be cataloged"""

    __implements__ = (IMemberDataTool)

    id = 'portal_memberdata'
    meta_type = 'PlonePAS-aware Catalog MemberData Tool'
    _properties = ()

    security = AccessControl.ClassSecurityInfo()

    manage_options=( ({'label' : 'Overview',
                       'action' : 'manage_overview'
                       },
                      {'label' : 'Contents Summary',
                       'action' : 'manage_showContents'
                       }
                      )
                     + BTreeFolder2.manage_options
                     )

    #
    #   ZMI methods
    #
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = PageTemplateFile('zpt/explainCatalogMemberDataTool', globals())

    security.declareProtected(ViewManagementScreens, 'manage_showContents')
    manage_showContents = PageTemplateFile('zpt/memberdataContents', globals())


    def __init__(self):
        BTreeFolder2.__init__(self)
        # Defaults from CMFCore.MemberDataTool
        self._setProperty('email', '', 'string')
        self._setProperty('portal_skin', '', 'string')
        self._setProperty('listed', '', 'boolean')
        self._setProperty('login_time', '2000/01/01', 'date')
        self._setProperty('last_login_time', '2000/01/01', 'date')

        # Compatibility with Plone's MemberData tool
        self.portraits=BTreeFolder2(id='portraits')

    #
    # CMFCore compatibility methods
    #
    security.declarePrivate('registerMemberData')
    def registerMemberData(self, m, id):
        '''
        Adds the given member data
        This is done as late as possible to avoid side effect
        transactions and to reduce the necessary number of
        entries.
        '''
        self._setObject(id, m)

    security.declarePrivate('deleteMemberData')
    def deleteMemberData(self, member_id):
        """ Delete member data of specified member."""
        
        try:
            self._delObject(member_id)
            try:
                from Products.PlonePAS.tools.memberdata.MemberDataTool import MemberDataTool as PASMDTool
                PASMDTool.deleteMemberData(member_id)
            except ImportError:
                pass
        except KeyError:
            return 0
        else:
            return 1

    #
    # IMemberDataTool interface fulfillment
    #

    security.declarePrivate('wrapUser')
    def wrapUser(self, u):
        '''
        If possible, returns the Member object that corresponds
        to the given User object.
        '''
        id = u.getId()
        m = self.get(id)
        if m is None:
            m = MemberData(id)
            self._setObject(id, m)
            
        # Return a wrapper with self as containment and
        # the user as context.
        return m.__of__(self).__of__(u)

    security.declareProtected(ManagePortal, 'getMemberDataContents')
    def getMemberDataContents(self):
        '''
        Returns a list containing a dictionary with information 
        about the BTree contents: member_count is the 
        total number of member instances stored in the memberdata-
        tool while orphan_count is the number of member instances 
        that for one reason or another are no longer in the 
        underlying acl_users user folder.
        The result is designed to be iterated over in a dtml-in
        '''
        member_ids = self.objectIds()

        membertool = getToolByName(self, 'portal_membership')
        user_ids = membertool.listMemberIds()
        orphan_ids = [m for m in member_ids if m not in user_ids]

        return [{
            'member_count' : len(member_ids),
            'orphan_count' : len(orphan_ids)
            }]


    security.declarePrivate('searchMemberDataContents')
    def searchMemberDataContents(self, search_param, search_term):
        """Backward-compatible search.  Deprecated: use member_catalog instead"""
        cat = getToolByName(self, MEMBER_CATALOG)

        if search_param == 'username':
            search_param = 'getUserName'

        if search_param not in cat.indexes():
            raise ValueError, "Cannot search members by %s: not indexed in member catalog" % search_param

        query = {search_param:search_term}
        results = cat(**query)

        return [{'username':r.getUserName, 'email':r.email} for r in results]

    security.declareProtected(ManagePortal, 'pruneMemberDataContents')
    def pruneMemberDataContents(self):
        '''
        Compare the user IDs stored in the member data
        tool with the list in the actual underlying acl_users
        and delete anything not in acl_users
        '''
        membertool= getToolByName(self, 'portal_membership')
        user_ids = membertool.listMemberIds()

        for m in self.objectIds():
            if m not in user_ids:
                self._delObject(m)

        # Portrait code for compatibility with Plone's MemberData tool
        for m in self.portraits.objectIds():
            if m not in user_ids:
                self.portraits._delObject(m)

    #
    # Compatibilty with Plone (code copied from CMFPlone.MemberDataTool)
    #
    def _getPortrait(self, member_id):
        "return member_id's portrait if you can "
        return self.portraits.get(member_id, None)

    def _setPortrait(self, portrait, member_id):
        " store portrait which must be a raw image in _portrais "
        if self.portraits.has_key(member_id):
            self.portraits._delObject(member_id)
        self.portraits._setObject(id= member_id, object=portrait)

    def _deletePortrait(self, member_id):
        " remove member_id's portrait "
        if self.portraits.has_key(member_id):
            self.portraits._delObject(member_id)


InitializeClass(MemberDataTool)

class MemberData(BaseMemberData):

    __implements__ = IMemberData

    security = AccessControl.ClassSecurityInfo()

    def __init__(self, id):
        self.id = id

    def getId(self):
        """Override to return the id we've stored"""
        return self.id

    security.declarePrivate('notifyModified')
    def notifyModified(self):
        # Recatalog this member
        cat = getToolByName(self, MEMBER_CATALOG)
        cat.catalog_object(self)

    security.declarePublic('getUser')
    def getUser(self):
        # First try using the acqusition context
        user = aq_parent(self)
        bcontext = aq_base(user)
        bcontainer = aq_base(aq_parent(aq_inner(self)))
        if bcontext is bcontainer or not hasattr(bcontext, 'getUserName'):
            # OK, the wrapper didn't work so let's try looking up the user by ID
            user_folder = getToolByName(self, 'acl_users')
            user = user_folder.getUser(self.getId())

        if user:
            return user
        else:
            raise 'MemberDataError', "Can't find user data for %s" % self.getId()

    def getTool(self):
        return getToolByName(self, 'portal_memberdata')


    security.declarePublic('getMemberId')
    def getMemberId(self):
        return self.getId()

# Backwards compatibility
XUFMemberData = MemberData

InitializeClass(MemberData)
