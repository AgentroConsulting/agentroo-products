/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { ImageField, imageField } from "@web/views/fields/image/image_field";
import { useState } from "@odoo/owl";

function loadImage(src) {
    return new Promise((resolve, reject) => {
        const image = new Image();
        image.crossOrigin = "anonymous";
        image.onload = () => resolve(image);
        image.onerror = reject;
        image.src = src;
    });
}

function canvasToBlob(canvas, type = "image/png") {
    return new Promise((resolve, reject) => {
        canvas.toBlob((blob) => {
            blob ? resolve(blob) : reject(new Error("Unable to prepare image."));
        }, type);
    });
}

async function copyImageToClipboard(field) {
    if (!field.props.record.data[field.props.name] || !field.state.isValid) {
        field.notification.add(_t("No image available to copy."), { type: "warning" });
        return;
    }

    if (!navigator.clipboard || !window.ClipboardItem) {
        field.notification.add(_t("Your browser does not support image clipboard copy."), {
            type: "danger",
        });
        return;
    }

    try {
        const image = await loadImage(field.currentImageUrl);
        const canvas = document.createElement("canvas");
        canvas.width = image.naturalWidth || image.width;
        canvas.height = image.naturalHeight || image.height;

        const ctx = canvas.getContext("2d");
        ctx.drawImage(image, 0, 0);

        const blob = await canvasToBlob(canvas);
        await navigator.clipboard.write([new ClipboardItem({ [blob.type]: blob })]);
        field.notification.add(_t("Image copied to clipboard."), { type: "success" });
    } catch (error) {
        console.error("Unable to copy product image.", error);
        field.notification.add(_t("Unable to copy image to clipboard."), { type: "danger" });
    }
}

export class SaleLineProductImageField extends ImageField {
    static template = "agentroo_product_image_clipboard.SaleLineProductImageField";

    setup() {
        super.setup();
        this.imageState = useState({
            rotation: 0,
            isFlipped: false,
        });
    }

    get imageStyle() {
        const baseStyle = this.sizeStyle || "";
        const scaleX = this.imageState.isFlipped ? -1 : 1;
        return `${baseStyle} transform: rotate(${this.imageState.rotation}deg) scaleX(${scaleX});`;
    }

    get currentImageUrl() {
        return this.getUrl(this.props.previewImage || this.props.name);
    }

    rotateImage() {
        this.imageState.rotation += 90;
    }

    flipImage() {
        this.imageState.isFlipped = !this.imageState.isFlipped;
    }

    async copyImage() {
        await copyImageToClipboard(this);
    }
}

export class ProductCopyImageField extends ImageField {
    static template = "agentroo_product_image_clipboard.ProductCopyImageField";
    static props = {
        ...ImageField.props,
        copyButtonPosition: { type: String, optional: true },
    };

    get copyButtonClass() {
        return [
            "o_agentroo_product_copy_image_button",
            "btn",
            "btn-light",
            "position-absolute",
            "opacity-0",
            "opacity-100-hover",
            "m-1",
            "p-1",
            this.props.copyButtonPosition === "center"
                ? "o_agentroo_product_copy_image_button_center"
                : "o_agentroo_product_copy_image_button_bottom_end",
        ].join(" ");
    }

    get currentImageUrl() {
        return this.getUrl(this.props.previewImage || this.props.name);
    }

    async copyImage() {
        await copyImageToClipboard(this);
    }
}

registry.category("fields").add("agentroo_sale_line_product_image", {
    ...imageField,
    component: SaleLineProductImageField,
});

registry.category("fields").add("agentroo_product_copy_image", {
    ...imageField,
    component: ProductCopyImageField,
    extractProps: (params) => ({
        ...imageField.extractProps(params),
        copyButtonPosition: params.options.copy_button_position,
    }),
});
