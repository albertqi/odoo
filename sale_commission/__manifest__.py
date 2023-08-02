{
    'name': 'Sales Commissions',
    'summary': 'Adds sales commission tracking and management to the Odoo system.',
    'description': """Sales Commissions
    ====================
    The Sales Commissions module is a custom development that 
    extends the functionality of the Odoo system by 
    introducing a comprehensive sales commission tracking and 
    management system.""",
    'version': '1.0',
    'license': 'OPL-1',
    'author': 'Odoo Inc.',
    'website': 'https://www.odoo.com/',
    'category': 'Custom Development/Commissions',
    'depends': [
        'sale',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sale_commission_data.xml',
        'wizards/process_commission_wizard_views.xml',
        'views/account_move_views_inherit.xml',
        'views/account_payment_views_inherit.xml',
        'views/product_category_views_inherit.xml',
        'views/report_sale_commission.xml',
        'views/sale_commission_menuitems.xml',
        'views/sale_commission_report.xml',
        'views/sale_commission_type_views.xml',
        'views/sale_commission_views.xml',
        'views/sale_order_views_inherit.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'sale_commission/static/src/css/report_sale_commission.css',
        ],
    },
    'auto_install': True,
    'application': True,
}
