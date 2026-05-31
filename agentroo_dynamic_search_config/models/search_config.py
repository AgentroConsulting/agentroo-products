from uuid import uuid4

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


SEARCHABLE_FIELD_TYPES = {
    "boolean",
    "char",
    "date",
    "datetime",
    "float",
    "html",
    "integer",
    "many2many",
    "many2one",
    "monetary",
    "selection",
    "text",
}
GROUPABLE_FIELD_TYPES = {
    "boolean",
    "char",
    "date",
    "datetime",
    "many2one",
    "selection",
}
DATE_FILTER_TYPES = [
    ("today", "Today"),
    ("this_week", "This Week"),
    ("this_month", "This Month"),
    ("last_month", "Last Month"),
    ("this_quarter", "This Quarter"),
    ("this_year", "This Year"),
    ("last_30_days", "Last 30 Days"),
]


class DynamicSearchConfig(models.Model):
    _name = "dynamic.search.config"
    _description = "Dynamic Search Configuration"
    _order = "name"
    _rec_name = "name"
    _sql_constraints = [
        ("agentroo_dynamic_search_config_model_unique", "unique(model_id)", "Only one configuration is allowed per model."),
    ]

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    model_id = fields.Many2one(
        "ir.model",
        required=True,
        domain=[("transient", "=", False), ("abstract", "=", False)],
        ondelete="cascade",
    )
    model_name = fields.Char(related="model_id.model", store=True, readonly=True)
    note = fields.Text()
    cache_token = fields.Char(default=lambda self: uuid4().hex, copy=False, readonly=True, required=True)
    filter_ids = fields.One2many("dynamic.search.filter", "config_id", string="Filters")
    groupby_ids = fields.One2many("dynamic.search.groupby", "config_id", string="Group By")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._dynamic_search_refresh_views()
        return records

    def write(self, vals):
        result = super().write(vals)
        if not self.env.context.get("dynamic_search_skip_refresh") and any(key != "cache_token" for key in vals):
            self._dynamic_search_after_change(touch=not self.env.context.get("dynamic_search_skip_touch"))
        return result

    def unlink(self):
        result = super().unlink()
        self.env["ir.ui.view"]._dynamic_search_clear_caches()
        return result

    def action_apply_reload_views(self):
        self.ensure_one()
        self._dynamic_search_refresh_views()
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

    def action_open_validator(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Validate Configuration"),
            "res_model": "dynamic.search.validator",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_config_id": self.id,
            },
        }

    def _run_validation(self):
        self.ensure_one()
        issues = []
        warnings = []

        if not self.filter_ids and not self.groupby_ids:
            warnings.append(_("No filters or group by entries are configured."))

        for entry in self.filter_ids:
            entry_issues, entry_warnings = entry._validate_entry()
            issues.extend(entry_issues)
            warnings.extend(entry_warnings)

        for entry in self.groupby_ids:
            entry_issues, entry_warnings = entry._validate_entry()
            issues.extend(entry_issues)
            warnings.extend(entry_warnings)

        return {
            "issues": issues,
            "warnings": warnings,
            "valid": not issues,
        }

    def _dynamic_search_refresh_views(self):
        self.env["ir.ui.view"]._dynamic_search_clear_caches()

    def _dynamic_search_after_change(self, touch=True):
        if touch:
            self._dynamic_search_touch()
        self._dynamic_search_refresh_views()

    def _dynamic_search_touch(self):
        for record in self:
            super(DynamicSearchConfig, record.with_context(
                dynamic_search_skip_refresh=True,
                dynamic_search_skip_touch=True,
            )).write({"cache_token": uuid4().hex})

    @api.onchange("model_id")
    def _onchange_model_id(self):
        for record in self:
            if record.model_id and not record.name:
                record.name = _("%s Search Configuration") % record.model_id.name

    @api.constrains("model_id")
    def _check_model_id(self):
        for record in self:
            model = self.env.get(record.model_name)
            if model is None:
                raise ValidationError(_("The selected model is not available in the registry."))
            if getattr(model, "_abstract", False):
                raise ValidationError(_("Abstract models cannot be configured for dynamic search options."))


class DynamicSearchFilter(models.Model):
    _name = "dynamic.search.filter"
    _description = "Dynamic Search Filter"
    _order = "sequence, id"

    config_id = fields.Many2one("dynamic.search.config", required=True, ondelete="cascade")
    config_model_id = fields.Many2one(
        "ir.model",
        related="config_id.model_id",
        readonly=True,
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    line_type = fields.Selection(
        [("filter", "Filter"), ("separator", "Separator")],
        default="filter",
        required=True,
    )
    field_id = fields.Many2one(
        "ir.model.fields",
        string="Field",
        domain="[('model_id', '=', config_model_id), ('store', '=', True)]",
        ondelete="cascade",
    )
    field_name = fields.Char(related="field_id.name", store=True, readonly=True)
    field_type = fields.Selection(related="field_id.ttype", readonly=True)
    filter_type = fields.Selection(
        [("domain", "Domain"), ("date", "Date"), ("boolean", "Boolean")],
        default="domain",
        required=True,
    )
    domain = fields.Char(help="Example: [('state', '=', 'draft')]")
    date_filter_type = fields.Selection(DATE_FILTER_TYPES)
    help = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.mapped("config_id")._dynamic_search_after_change()
        return records

    def write(self, vals):
        configs = self.mapped("config_id")
        result = super().write(vals)
        (configs | self.mapped("config_id"))._dynamic_search_after_change()
        return result

    def unlink(self):
        configs = self.mapped("config_id")
        result = super().unlink()
        configs._dynamic_search_after_change()
        return result

    @api.constrains("line_type", "field_id", "filter_type", "domain", "date_filter_type")
    def _check_configuration(self):
        for record in self:
            issues, _warnings = record._validate_entry()
            if issues:
                raise ValidationError("\n".join(issues))

    def _validate_entry(self):
        self.ensure_one()
        issues = []
        warnings = []
        if self.line_type == "separator":
            return issues, warnings
        if not self.field_id:
            issues.append(_("%s: field is required.") % self.name)
            return issues, warnings
        if self.field_id.model_id != self.config_id.model_id:
            issues.append(_("%s: field must belong to model %s.") % (self.name, self.config_id.model_id.display_name))
        if not self.field_id.store:
            issues.append(_("%s: only stored fields are supported.") % self.name)
        if self.field_id.ttype not in SEARCHABLE_FIELD_TYPES:
            issues.append(_("%s: field type %s is not supported for filters.") % (self.name, self.field_id.ttype))
        if self.filter_type == "domain":
            if not self.domain:
                issues.append(_("%s: domain is required for domain filters.") % self.name)
            else:
                try:
                    value = safe_eval(self.domain, {"uid": self.env.uid})
                except Exception as exc:
                    issues.append(_("%s: invalid domain syntax: %s") % (self.name, exc))
                else:
                    if not isinstance(value, (list, tuple)):
                        issues.append(_("%s: domain must evaluate to a list or tuple.") % self.name)
                    if len(str(self.domain)) > 180:
                        warnings.append(_("%s: complex domains can affect search performance.") % self.name)
        elif self.filter_type == "date":
            if self.field_id.ttype not in ("date", "datetime"):
                issues.append(_("%s: date filters require a date or datetime field.") % self.name)
            if not self.date_filter_type:
                issues.append(_("%s: date period is required.") % self.name)
        elif self.filter_type == "boolean":
            if self.field_id.ttype != "boolean":
                issues.append(_("%s: boolean filters require a boolean field.") % self.name)
        return issues, warnings


class DynamicSearchGroupBy(models.Model):
    _name = "dynamic.search.groupby"
    _description = "Dynamic Search Group By"
    _order = "sequence, id"

    config_id = fields.Many2one("dynamic.search.config", required=True, ondelete="cascade")
    config_model_id = fields.Many2one(
        "ir.model",
        related="config_id.model_id",
        readonly=True,
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    line_type = fields.Selection(
        [("groupby", "Group By"), ("separator", "Separator")],
        default="groupby",
        required=True,
    )
    field_id = fields.Many2one(
        "ir.model.fields",
        string="Field",
        domain="[('model_id', '=', config_model_id), ('store', '=', True)]",
        ondelete="cascade",
    )
    field_name = fields.Char(related="field_id.name", store=True, readonly=True)
    field_type = fields.Selection(related="field_id.ttype", readonly=True)
    date_groupby = fields.Selection(
        [
            ("day", "Day"),
            ("week", "Week"),
            ("month", "Month"),
            ("quarter", "Quarter"),
            ("year", "Year"),
        ]
    )
    help = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.mapped("config_id")._dynamic_search_after_change()
        return records

    def write(self, vals):
        configs = self.mapped("config_id")
        result = super().write(vals)
        (configs | self.mapped("config_id"))._dynamic_search_after_change()
        return result

    def unlink(self):
        configs = self.mapped("config_id")
        result = super().unlink()
        configs._dynamic_search_after_change()
        return result

    @api.constrains("line_type", "field_id", "date_groupby")
    def _check_configuration(self):
        for record in self:
            issues, _warnings = record._validate_entry()
            if issues:
                raise ValidationError("\n".join(issues))

    def _validate_entry(self):
        self.ensure_one()
        issues = []
        warnings = []
        if self.line_type == "separator":
            return issues, warnings
        if not self.field_id:
            issues.append(_("%s: field is required.") % self.name)
            return issues, warnings
        if self.field_id.model_id != self.config_id.model_id:
            issues.append(_("%s: field must belong to model %s.") % (self.name, self.config_id.model_id.display_name))
        if not self.field_id.store:
            issues.append(_("%s: only stored fields are supported.") % self.name)
        if self.field_id.ttype not in GROUPABLE_FIELD_TYPES:
            issues.append(_("%s: field type %s is not supported for group by.") % (self.name, self.field_id.ttype))
        if self.date_groupby and self.field_id.ttype not in ("date", "datetime"):
            issues.append(_("%s: date interval grouping requires a date or datetime field.") % self.name)
        if self.field_id.ttype in ("date", "datetime") and not self.date_groupby:
            warnings.append(_("%s: date field will use the default server interval.") % self.name)
        return issues, warnings
