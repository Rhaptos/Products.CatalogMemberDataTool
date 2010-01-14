
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName

def createTool(context):
    if context.readDataFile('create-catalogmdtool.txt') is None:
        return
    logger = context.getLogger('create-catalogmdtool')
    portal = context.getSite()
    portal_membership = getToolByName(portal, 'portal_membership')

    orig_md = getToolByName(portal, 'portal_memberdata', None)
    if orig_md is not None:
        portal.manage_delObjects(['portal_memberdata'])
        logger.info('Removed old portal_memberdata tool')

    portal.manage_addProduct['CatalogMemberDataTool'].manage_addTool(
            'PlonePAS-aware Catalog MemberData Tool', None)
    md = getToolByName(portal, 'portal_memberdata')
    logger.info('Added Catalog MemberData tool')

    # Migrate old data
    if orig_md is not None:
        md._properties = aq_base(getattr(orig_md, '_properties'))
        property_ids = orig_md.propertyIds()
        for attr in property_ids:
            setattr(md, attr, aq_base(getattr(aq_base(orig_md), attr)))

        logger.info("Migrated Member Properties")

        # Migrate members
        try:
            old_members = aq_base(getattr(orig_md, '_members'))
        except AttributeError:
            # No _members attribute.  Perhaps this was already a Catalog 
            # MemberData Tool
            old_members = aq_base(getattr(orig_md, '_tree'))
        for member_id, obj in old_members.items():
            # We have to create new objects: could take a while
            new_obj = portal_membership.getMemberById(member_id)
            props = {}
            for prop in property_ids:
                value = new_obj.getProperty(prop) or getattr(obj, prop, None)
                if value is not None:
                    props[prop] = value
            new_obj.setMemberProperties(props)

        logger.info("Migrated Member Data")

    catalog = portal.member_catalog
    catalog.manage_catalogClear()
    logger.info('Cleared existing Member Catalog')

    for m in md.objectValues():
        try:
            catalog.catalog_object(m)
        except 'MemberDataError', e:
            logger.error(e)
    logger.info('Cataloged existing member')



