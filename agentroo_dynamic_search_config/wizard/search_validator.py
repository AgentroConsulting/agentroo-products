from odoo import _, fields, models


class DynamicSearchValidator(models.TransientModel):
    _name = "dynamic.search.validator"
    _description = "Dynamic Search Validator"

    config_id = fields.Many2one("dynamic.search.config", required=True, readonly=True)
    result = fields.Text(readonly=True)
    is_valid = fields.Boolean(readonly=True)

    def action_validate(self):
        self.ensure_one()
        outcome = self.config_id._run_validation()
        lines = []
        if outcome["valid"]:
            lines.append(_("Validation passed."))
        else:
            lines.append(_("Validation failed."))
        if outcome["issues"]:
            lines.append("")
            lines.append(_("Errors:"))
            lines.extend(f"- {issue}" for issue in outcome["issues"])
        if outcome["warnings"]:
            lines.append("")
            lines.append(_("Warnings:"))
            lines.extend(f"- {warning}" for warning in outcome["warnings"])
        self.write({
            "result": "\n".join(lines),
            "is_valid": outcome["valid"],
        })
        return {
            "type": "ir.actions.act_window",
            "name": _("Validate Configuration"),
            "res_model": "dynamic.search.validator",
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }
