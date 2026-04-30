Agentroo Product Image Clipboard
================================

Agentroo Product Image Clipboard helps users copy product images from sale
order lines, product forms, product detail pages, kanban views, and catalog
views (`agentroo_product_image_clipboard`).

It also displays product images on sale order lines and sale order reports to
make product identification easier during sales operations.

Configuration
=============

* No additional configurations needed.

Odoo modules dependencies
=========================

* Base (`base`)
* Sales (`sale_management`)

Features
========

* Copy product images from sale order lines.
* Copy product images from product template and product variant forms.
* Copy product images from product kanban and catalog views.
* Rotate and flip product images in sale order lines.
* Display product images on sale order lines.
* Display product images on printed sale order reports.

Technical Details
=================

* Related image field on sale order line: `product_image_128`
* Sale order line image widget: `agentroo_sale_line_product_image`
* Product image copy widget: `agentroo_product_copy_image`

UI Testing
==========

* Copy image from a sale order line.
* Rotate and flip image from a sale order line.
* Copy image from product template form.
* Copy image from product variant/detail form.
* Copy image from product kanban view.
* Copy image from product catalog view.
* Print a sale order and confirm the product image is visible in the report.

Clipboard copy depends on browser permissions and must be tested through a real
user click in the browser.

Company
-------

* Agentroo Consultings

Contacts
--------

* Mail Contact: agentrooconsultings@gmail.com

Source Code Revision
--------------------

* Community: Not specified
* Enterprise: Not specified

Bug Tracker
-----------

Please feel free to contact us using the provided details for any issues or
concerns related to this module.

Maintainer
==========

Agentroo Consultings provides Odoo implementation, customization, development,
migration, integration, and support services.
