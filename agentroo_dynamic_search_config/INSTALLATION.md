# Installation Guide

## Requirements

- Odoo 18 compatible server environment
- `base`, `web`, and `sale` installed

## Steps

1. Copy `agentroo_dynamic_search_config` into an addons path.
2. Restart the Odoo service.
3. Update the apps list from the Apps menu.
4. Install the module.

## Validation

1. Open `Dynamic Search -> Search Configurations`.
2. Confirm the demo sales order configuration exists if demo data is enabled.
3. Open the configuration and run `Validate`.
4. Click `Apply & Reload Views`.
5. Open Sales orders and confirm the injected search entries appear.

## Troubleshooting

- If no changes appear, verify the configuration is active.
- If validation fails, inspect the domain syntax and field types.
- If demo data fails to load, confirm the `sale` module is installed.
