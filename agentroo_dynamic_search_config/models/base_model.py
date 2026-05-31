from datetime import datetime, time, timedelta

from lxml import etree
import pytz

from odoo import api, fields, models


class BaseModel(models.AbstractModel):
    _inherit = "base"

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type="form", **options):
        key = super()._get_view_cache_key(view_id=view_id, view_type=view_type, **options)
        if view_type != "search":
            return key
        config = self._dynamic_search_get_config()
        if not config:
            return key + (False,)
        return key + ((config.id, config.cache_token),)

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id=view_id, view_type=view_type, **options)
        if view_type != "search":
            return arch, view

        config = self._dynamic_search_get_config()
        if not config:
            return arch, view
        return self._dynamic_search_inject_arch(arch, config), view

    @api.model
    def _dynamic_search_get_config(self):
        return self.env["dynamic.search.config"].sudo().search(
            [("model_name", "=", self._name), ("active", "=", True)],
            limit=1,
        )

    @api.model
    def _dynamic_search_inject_arch(self, arch, config):
        if isinstance(arch, etree._Element):
            root = etree.fromstring(etree.tostring(arch))
        else:
            root = etree.fromstring(arch.encode("utf-8"))
        self._dynamic_search_append_filters(root, config)
        self._dynamic_search_append_groupby(root, config)
        if isinstance(arch, etree._Element):
            return root
        return etree.tostring(root, encoding="unicode")

    @api.model
    def _dynamic_search_append_filters(self, root, config):
        entries = config.filter_ids.filtered("active").sorted(key=lambda r: (r.sequence, r.id))
        if not entries:
            return

        root.append(etree.Element("separator"))
        for entry in entries:
            if entry.line_type == "separator":
                root.append(etree.Element("separator"))
                continue
            node = etree.Element(
                "filter",
                name=f"dynamic_filter_{entry.id}",
                string=entry.name,
            )
            if entry.help:
                node.set("help", entry.help)
            if entry.filter_type == "domain":
                node.set("domain", entry.domain or "[]")
            elif entry.filter_type == "boolean":
                node.set("domain", repr([(entry.field_name, "=", True)]))
            elif entry.filter_type == "date":
                node.set("domain", self._dynamic_search_date_domain(entry))
            root.append(node)

    @api.model
    def _dynamic_search_append_groupby(self, root, config):
        entries = config.groupby_ids.filtered("active").sorted(key=lambda r: (r.sequence, r.id))
        if not entries:
            return

        group = root.xpath("./group[@name='group_by']")[:1]
        if group:
            group_node = group[0]
        else:
            group_node = etree.Element("group", string="Group By", name="group_by")
            root.append(group_node)

        group_node.append(etree.Element("separator"))
        for entry in entries:
            if entry.line_type == "separator":
                group_node.append(etree.Element("separator"))
                continue
            group_by = entry.field_name
            if entry.date_groupby:
                group_by = f"{group_by}:{entry.date_groupby}"
            node = etree.Element(
                "filter",
                name=f"dynamic_groupby_{entry.id}",
                string=entry.name,
                context=repr({"group_by": group_by}),
            )
            if entry.help:
                node.set("help", entry.help)
            group_node.append(node)

    @api.model
    def _dynamic_search_date_domain(self, entry):
        today = fields.Date.context_today(self)
        start = end = today
        period = entry.date_filter_type
        if period == "today":
            start = end = today
        elif period == "this_week":
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
        elif period == "this_month":
            start = today.replace(day=1)
            next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
            end = next_month - timedelta(days=1)
        elif period == "last_month":
            this_month = today.replace(day=1)
            end = this_month - timedelta(days=1)
            start = end.replace(day=1)
        elif period == "this_quarter":
            quarter_month = ((today.month - 1) // 3) * 3 + 1
            start = today.replace(month=quarter_month, day=1)
            if quarter_month == 10:
                end = start.replace(year=start.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end = start.replace(month=quarter_month + 3, day=1) - timedelta(days=1)
        elif period == "this_year":
            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)
        elif period == "last_30_days":
            start = today - timedelta(days=29)
            end = today

        if entry.field_type == "datetime":
            domain = self._dynamic_search_datetime_domain(entry, start, end)
        else:
            domain = [
                (entry.field_name, ">=", fields.Date.to_string(start)),
                (entry.field_name, "<=", fields.Date.to_string(end)),
            ]
        return repr(domain)

    @api.model
    def _dynamic_search_datetime_domain(self, entry, start, end):
        user_tz = self.env.user.tz or "UTC"
        try:
            timezone = pytz.timezone(user_tz)
        except pytz.UnknownTimeZoneError:
            timezone = pytz.UTC

        start_value = self._dynamic_search_local_to_utc(timezone, datetime.combine(start, time.min))
        end_value = self._dynamic_search_local_to_utc(timezone, datetime.combine(end, time.max.replace(microsecond=0)))
        return [
            (entry.field_name, ">=", fields.Datetime.to_string(start_value)),
            (entry.field_name, "<=", fields.Datetime.to_string(end_value)),
        ]

    @api.model
    def _dynamic_search_local_to_utc(self, timezone, value):
        try:
            localized = timezone.localize(value, is_dst=None)
        except (pytz.AmbiguousTimeError, pytz.NonExistentTimeError):
            localized = timezone.localize(value, is_dst=False)
        return localized.astimezone(pytz.UTC).replace(tzinfo=None)
