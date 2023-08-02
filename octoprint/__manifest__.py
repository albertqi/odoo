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
        'security/octoprint_groups.xml',
        'security/ir.model.access.csv',
        
        'views/mrp_production_views_inherit.xml',
        'views/octoproint_menuitems.xml',
        'views/octoprint_print_views.xml',
        'views/octoprint_printer_views.xml',
    ],
    'application': True
}
