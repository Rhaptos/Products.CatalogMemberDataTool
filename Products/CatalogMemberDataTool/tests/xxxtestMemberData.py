#
# MemberDataTool tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

ZopeTestCase.installProduct('CatalogMemberDataTool')
ZopeTestCase.installProduct('ZCatalog')

from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy

from OFS.Image import Image
default_user = PloneTestCase.default_user

from Products.CatalogMemberDataTool.MemberDataTool import MemberData

class TestMemberDataTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.portal.portal_quickinstaller.installProduct('CatalogMemberDataTool')
        self.memberdata = self.portal.portal_memberdata

    def testInterface(self):
        """MemberDataTool must implement IMemberDataTool"""
        from Products.CMFCore.interfaces.portal_memberdata import MemberData as IMemberData
        self.failUnless(IMemberData.isImplementedByInstancesOf(MemberData))
    """            
    def testGetUser(self):
        #getUser() must return correct user object for a wrapped MemberData
        m = MemberData(default_user)
        self.memberdata.registerMemberData(m, default_user)
        u = self.portal.acl_users.getUser(default_user)
        wrapper = self.memberdata.wrapUser(u)
        self.assertEquals(wrapper.getUser().getId(), u.getId())
    
    def testGetPropertyDefault(self):
        #getProperty() should return the default when the property cannot be found
        m = MemberData(default_user)
        self.memberdata.registerMemberData(m, default_user)
        u = self.portal.acl_users.getUser(default_user)
        wrapper = self.memberdata.wrapUser(u)
        self.assertEquals(wrapper.getProperty('foo', 'bar'), 'bar')
    """
    # FIXME: We need a lot more tests for the different cases of getProperty

    def testSetMemberProperties(self):
        m = MemberData(default_user)
        self.memberdata.registerMemberData(m, default_user)
        u = self.portal.acl_users.getUser(default_user)
        wrapper = self.memberdata.wrapUser(u)

        fullname = 'Bob Smith'
        email = 'bob@example.com'

        wrapper.setMemberProperties({'fullname':fullname, 'email':email})
        self.assertEquals(wrapper.getProperty('fullname'), fullname)
        self.assertEquals(wrapper.getProperty('email'), email)
        
    
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMemberDataTool))
    return suite

if __name__ == '__main__':
    framework()
