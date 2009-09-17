from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from Acquisition import aq_base
from zExceptions import BadRequest

from Products.CatalogMemberDataTool import product_globals
from Products.CatalogMemberDataTool.MemberDataTool import MemberData

class Empty: pass

def create_catalog(portal):
    from Products.ZCTextIndex.ZCTextIndex import PLexicon, ZCTextIndex
    from Products.ZCTextIndex.Lexicon import CaseNormalizer, StopWordAndSingleCharRemover
    from Products.ZCTextIndex.HTMLSplitter import HTMLWordSplitter

    portal.manage_addProduct['ZCatalog'].manage_addZCatalog('member_catalog', 'MemberData catalog')
    catalog = portal.member_catalog
    lexicon = PLexicon('lexicon', '' , HTMLWordSplitter(), CaseNormalizer(), StopWordAndSingleCharRemover())
    catalog._setObject('lexicon', lexicon)

    ZCText_extras = Empty()
    ZCText_extras.doc_attr = 'fullname'
    ZCText_extras.index_type = 'Okapi BM25 Rank'
    ZCText_extras.lexicon_id = 'lexicon'
    catalog.addIndex('fullname', 'ZCTextIndex', ZCText_extras)

    catalog.addIndex('email', 'FieldIndex')
    catalog.addIndex('getGroups', 'KeywordIndex')
    catalog.addIndex('getUserName', 'FieldIndex')
    catalog.addIndex('last_login_time', 'DateIndex')
    catalog.addIndex('listed', 'FieldIndex')
    catalog.addIndex('login_time', 'DateIndex')

    catalog.addColumn('email')
    catalog.addColumn('fullname')
    catalog.addColumn('getGroups')
    catalog.addColumn('getId')
    catalog.addColumn('getUserName')
    catalog.addColumn('status')

    return catalog

def install(self):
    """Add the tool"""
    out = StringIO()

    # Add the tool
    urltool = getToolByName(self, 'portal_url')
    portal = urltool.getPortalObject();
    mship = getToolByName(self, 'portal_membership')

    try:
        orig_md = getToolByName(portal, 'portal_memberdata')
        portal.manage_delObjects('portal_memberdata')
        out.write("Removed old portal_memberdata tool\n")
    except BadRequest:
        pass
    
    portal.manage_addProduct['CatalogMemberDataTool'].manage_addTool('PlonePAS-aware Catalog MemberData Tool', None)
    md = getToolByName(portal, 'portal_memberdata')
    out.write("Added Catalog MemberData Tool\n")

    # Migrate old data
    if orig_md is not None:
        md._properties = aq_base(getattr(orig_md, '_properties'))
        property_ids = orig_md.propertyIds()
        for attr in property_ids:
            setattr(md, attr, aq_base(getattr(aq_base(orig_md), attr)))

        out.write("Migrated Member Properties\n")

        # Migrate members
        try:
            old_members = aq_base(getattr(orig_md, '_members'))
        except AttributeError:
            # No _members attribute.  Perhaps this was already a Catalog MemberData Tool
            old_members = aq_base(getattr(orig_md, '_tree'))
        for member_id, obj in old_members.items():
            # We have to create new objects: could take a while
            new_obj = mship.getMemberById(member_id)
            props = {}
            for prop in property_ids:
                value = new_obj.getProperty(prop) or getattr(obj, prop, None)
                if value is not None:
                    props[prop] = value
            new_obj.setMemberProperties(props)

        out.write("Migrated Member Data\n")


        
    if not getattr(portal, 'member_catalog',None):
        catalog = create_catalog(portal)
        out.write("Created Member Catalog\n")
    else:
        catalog = portal.member_catalog
        catalog.manage_catalogClear()
        out.write("Cleared existing Member Catalog\n")

    for m in md.objectValues():
        try:
            catalog.catalog_object(m)
        except 'MemberDataError', e:
            print e
    out.write("Cataloged existing members\n")

    return out.getvalue()
