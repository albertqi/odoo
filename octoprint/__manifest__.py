{
    'name': 'OctoPrint Integration',
    'summary': 'Adds OctoPrint integration to the Odoo system.',
    'description': """OctoPrint Integration
====================
The OctoPrint Integration module is a custom development that
extends the functionality of the Odoo system by
integrating OctoPrint with the manufacturing application.""",
    'version': '1.0',
    'license': 'OPL-1',
    'author': 'Odoo Inc.',
    'website': 'https://www.odoo.com/',
    'category': 'Custom Development/Printing',
    'depends': [
        'mrp',
    ],
    'data': [
        'views/mrp_production_views_inherit.xml',
    ],
}
