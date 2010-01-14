CatalogMemberDataTool

  This tool replaces CMFCore's stock MemberData Tool for one purpose:
  the ability to catalog member data for fast searching.  It
  accomplishes this by turning the tool into a container (a
  BTreeFolder2 to be specific) and storing the member data objects
  inside.  That way they can be indexed.

  Why not use CMFMember?  While CMFMember does include a member
  catalog, it also adds some complexity like Archetypes and
  member-workflow that we didn't need or want.  In the interest of
  compatibility we did use the same 'member_catalog' name to make it
  easy for people to migrate to CMFMember.

  CatalogMemberDataTool is compatible with, but does not require Plone.
  If you are using CatalogMemberDataTool with GroupUserFolder you must
  use either version 2.0.2 or the development trunk.

  Notes:

    - MemberData properties are still editable through the Properties
      tab, however you will need to make any changes the
      member_catalog indexes (indices?) yourself.

    - searchMemberDataContents() is provided for compatibilty but
      applications should query the catalog directly instead

