# -*- coding: utf-8 -*-
# Part of Agentroo Consultings.
# See LICENSE file for full copyright and licensing details.

{
    'name': "Product Image Clipboard",
    'version': "18.0.1.0.0",
    'category': "Sales",
    'license': 'OPL-1',
    'summary': (
        "Copy product images from sale order lines, product forms, kanban "
        "views, and catalog views."
    ),
    'description': """
        Copy product images from sale order lines, product forms, product
        detail pages, kanban views, and catalog views.

        The module also keeps product images visible on sale order lines and
        sale order reports so users can identify products quickly.
    """,
    'author': "Agentroo Consultings",
    'depends': [
        'base',
        'sale_management'
    ],
    'data': [
        'report/sale_order_report.xml',
        'views/sale_order_views.xml',
        'views/product_template_views.xml',
        'views/product_product_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'agentroo_product_image_clipboard/static/src/js/sale_line_product_image_widget.js',
            'agentroo_product_image_clipboard/static/src/xml/sale_line_product_image_widget.xml',
            'agentroo_product_image_clipboard/static/src/scss/sale_line_product_image_widget.scss',
        ],
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'images': [
        'static/description/Banner.png',
        'static/description/img.png',
        'static/description/img_1.png',
    ],
}
