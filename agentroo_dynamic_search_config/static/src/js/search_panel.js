/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("actions").add("agentroo_dynamic_search_config.reload", async (env) => {
    return env.services.action.doAction({
        type: "ir.actions.client",
        tag: "reload",
    });
});
