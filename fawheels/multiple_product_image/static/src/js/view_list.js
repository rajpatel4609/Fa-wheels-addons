odoo.define('multiple_product_image.widget', function(require) {
    "use strict";

    var ControlPanelMixin = require('web.ControlPanelMixin');
    var core = require('web.core');
    var ListView = require('web.ListView');
    var Model = require('web.DataModel');
    var session = require('web.session');
    var Widget = require('web.Widget');
    var _t = core._t;
    var _lt = core._lt;
    var list = core.list_widget_registry;
    var utils = require('web.utils');
    var ColumnBinary = core.list_widget_registry.get('field').extend({
        /**
         * Return a link to the binary data as a file
         *
         * @private
         */
        _format: function(row_data, options) {
            var text = _t("Download"),
                filename = _t('Binary file');
            var value = row_data[this.id].value;
            if (!value) {
                return options.value_if_empty || '';
            }
            var download_url;
            if (value && value.substr(0, 10).indexOf(' ') == -1) {
                download_url = "data:application/octet-stream;base64," + value;
            } else {
                download_url = session.url('/web/content', {
                    model: options.model,
                    field: this.id,
                    id: options.id,
                    download: true
                });
                if (this.filename) {
                    download_url += '&filename_field=' + this.filename;
                }
            }
            if (this.filename && row_data[this.filename]) {
                text = _.str.sprintf(_t("Download \"%s\""), formats.format_value(
                    row_data[this.filename].value, {
                        type: 'char'
                    }));
                filename = row_data[this.filename].value;
            }
            if (options.model == 'product.images') {
                return _.template("<img width='160' src='<%-href%>'/>")({
                    href: download_url,
                });
            }
            return _.template('<a download="<%-download%>" href="<%-href%>"><%-text%></a> (<%-size%>)')({
                text: text,
                href: download_url,
                size: utils.binary_to_binsize(value),
                download: filename,
            });
        },

    });
    list.add("field.binary", ColumnBinary);


});