# Dynamic Search Configuration

Odoo 19 compatible module for dynamic search filter and group-by configuration.

This module adds an administration screen that lets system users configure extra search filters and group by entries per model without editing XML views.

## Features

- Domain, date, and boolean filters
- Configurable group by entries, including date intervals
- One active configuration per model
- Validation wizard for syntax and compatibility checks
- Immediate cache clearing through an apply-and-reload action

## Installation

1. Put the module in your addons path.
2. Update the apps list.
3. Install `Dynamic Search Configuration`.

## Usage

1. Open `Dynamic Search -> Search Configurations`.
2. Create a configuration for a model.
3. Add filter rows and group by rows.
4. Click `Validate`.
5. Click `Apply & Reload Views`.

## Notes

- Filters and group by definitions are appended to the existing search view.
- Only stored fields are supported.
- Date filters are converted to explicit date domains at runtime.
