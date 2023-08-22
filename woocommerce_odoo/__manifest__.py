# -*- coding: utf-8 -*-

{
  'name': 'Woo Odoo Connector Demo',
 'version': '15.0.1.0.0',
 'author': 'Mohamed Habib Challouf',
 'category': 'Tools',
 'depends': ['base',
             'product',
             'sale',
             'stock',
             'purchase'],
 
 'data': ['views/autentifcation_view.xml',
          'views/product_category.xml', 
          'views/product_product.xml', 
          'views/transcation_logs.xml'
          ],
          
    'installable': True,
    'application': False,
    'auto_install': True,
    'license': 'LGPL-3',
 
 }
