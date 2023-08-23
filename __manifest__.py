# -*- coding: utf-8 -*-
{
    'name': "Purchase",
    'version': '1.0.0',
    'sequence': -101,
    'summary': """ """,
    'description': """ """,
    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    'category': 'Sales',

    # any module necessary for this one to work correctly
    'depends': ['mail', 'product','purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/reject_purchase_request.xml',
        'wizard/purchase_order.xml',
        'report/purchase_request_report.xml',
        'report/report.xml',
        'views/menu.xml',
        'views/purchase_request_view.xml',
        'views/purchase_request_line_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3'
}
