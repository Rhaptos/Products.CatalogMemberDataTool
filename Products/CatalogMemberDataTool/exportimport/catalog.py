
from Products.GenericSetup.interfaces import IBody
from zope.component import queryMultiAdapter

filename = 'config-mdcatalog.xml'
def importCatalog(context):
    portal = context.getSite()
    body = context.readDataFile(filename)
    if body is None:
        logger = context.getLogger('config-mdcatalog')
        logger.info('Nothing to import')
        return
    importer = queryMultiAdapter((portal.member_catalog, context), IBody)
    if importer:
        importer.name = 'config-mdcatalog'
        importer.filename = filename
        importer.body = body


def exportCatalog(context):
    portal = context.getSite()
    if 'member_catalog' not in portal.objectIds():
        logger = context.getLogger('config-mdcatalog')
        logger.info('Nothing to export.')
        return
    exporter = queryMultiAdapter((portal.member_catalog, context), IBody)
    if exporter:
        exporter.name = 'config-mdcatalog'
        body = exporter.body
        if body is not None:
            context.writeDataFile(filename, body, exporter.mime_type)


def createCatalog(context):
    if context.readDataFile('create-mdcatalog.txt') is None:
        return
    logger = context.getLogger('create-mdcatalog')
    portal = context.getSite()
    if 'member_catalog' not in portal.objectIds():
        portal.manage_addProduct['ZCatalog'].manage_addZCatalog(
            'member_catalog', 'MemberData catalog')
        logger.info('Created Member Catalog')

