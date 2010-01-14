"""
Initialize CatalogMemberDataTool Product

Author: Brent Hendricks
(C) 2005 Rice University

This software is subject to the provisions of the GNU General
Public License Version 2 (GPL).  See LICENSE.txt for details.
"""

import sys
from Products.CMFCore import utils
import MemberDataTool
import PASMemberDataTool

this_module = sys.modules[ __name__ ]
product_globals = globals()
tools = ( MemberDataTool.MemberDataTool, PASMemberDataTool.MemberDataTool)


def initialize(context):
    utils.ToolInit('Catalog MemberData Tool',
                    tools = tools,
                    icon='tool.gif' 
                    ).initialize( context )
