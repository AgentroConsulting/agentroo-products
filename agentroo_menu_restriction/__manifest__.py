{
    'name': 'Agentroo User Menu Restriction',
    'version': '19.0.1.0.0',
    'summary': 'Restrict visible apps/menus per user',
    'description': """
        Per-user app/menu visibility control:
        - Add 'Allowed Apps' field on each user record
        - Leave empty to show all apps (no restriction)
        - Select specific apps to limit what that user can see
        - Changes take effect immediately (menu cache is cleared on save)
    """,
    'category': 'Administration',
    'author': 'Agentroo Consulting',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_users_views.xml',
    ],
    'images': [
        'static/description/main_screenshot.png',
        'static/description/Banner1.png',
        'static/description/allowed-app-result.png',
        'static/description/allowed-app-workflow.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
