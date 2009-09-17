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
        from Products.CMFCore.interfaces.portal_memberdata import portal_memberdata as IMemberDataTool
        self.failUnless(IMemberDataTool.isImplementedBy(self.memberdata))
                
    def testRegisterMemberData(self):
        """Verify """
        m = MemberData(default_user)
        self.memberdata.registerMemberData(m, default_user)


    def testDeleteMemberData(self):
        """Verify deleteMemberData"""
        m = MemberData(default_user)
        self.memberdata.registerMemberData(m, default_user)
        self.failUnless(self.memberdata.has_key(default_user) )
        self.failUnless(self.memberdata.deleteMemberData(default_user))
        self.failIf(self.memberdata.has_key(default_user) )
        self.failIf(self.memberdata.deleteMemberData(default_user))


    def testWrapUserReturnsMemberData(self):
        """wrapUser must return an instance of MemberData"""
        m = MemberData(default_user)
        self.memberdata.registerMemberData(m, default_user)

        u = self.portal.acl_users.getUser(default_user)
        wrapper = self.memberdata.wrapUser(u)
        self.failUnless(isinstance(wrapper, MemberData))

    def testWrapUserForNonUsers(self):
        """wrapUser must return an instance of MemberData even for non-existant users"""
        u = self.portal.acl_users.getUser(default_user)
        wrapper = self.memberdata.wrapUser(u)
        self.failUnless(isinstance(wrapper, MemberData))

    def testGetMemberDataContents(self):
        """getMemberDataContents should return the correct dictionary"""
        m = MemberData(default_user)
        self.memberdata.registerMemberData(m, default_user)

        n = MemberData('no_user')
        self.memberdata.registerMemberData(n, 'no_user')
        
        info = self.memberdata.getMemberDataContents()[0]
        self.assertEqual(info['member_count'], 2)
        self.assertEqual(info['orphan_count'], 1)

    def testPruneMemberDataContents(self):
        """pruneMemberDataContents must remove orphans"""
        m = MemberData(default_user)
        self.memberdata.registerMemberData(m, default_user)

        n = MemberData('no_user')
        self.memberdata.registerMemberData(n, 'no_user')

        self.memberdata.pruneMemberDataContents()
        info = self.memberdata.getMemberDataContents()[0]
        self.assertEqual(info['member_count'], 1)
        self.assertEqual(info['orphan_count'], 0)
        
    
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMemberDataTool))
    return suite

if __name__ == '__main__':
    framework()
