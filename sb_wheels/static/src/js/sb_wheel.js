odoo.define('sb_wheels.sb_wheels', function (require) {
var core = require('web.core');
var data = require('web.data');

var KanbanView = require('web_kanban.KanbanView');
var KanbanColumn = require('web_kanban.Column');
var quick_create = require('web_kanban.quick_create');

var ColumnQuickCreate = quick_create.ColumnQuickCreate;

var FBKanbanColumn = KanbanColumn.extend({
    view_type: "fb_team_dashboard",
    searchview_hidden: true,
    start: function() {
        var self = this;
        this.$header = this.$('.o_kanban_header');

        for (var i = 0; i < this.data_records.length; i++) {
            this.add_record(this.data_records[i], {no_update: true});
        }
        this.$header.tooltip();

        this.update_column();
        this.$el.click(function (event) {
            if (self.$el.hasClass('o_column_folded')) {
                event.preventDefault();
                self.folded = false;
                self.update_column();
            }
        });
    },
})

var FBDashboardView = KanbanView.extend({
    custom_events: {
        'kanban_record_open': 'open_record',
        'kanban_record_edit': 'edit_record',
        'kanban_record_delete': 'delete_record',
        'kanban_do_action': 'open_action',
        'kanban_reload': 'do_reload',
        'kanban_column_resequence': function (event) {
            this.resequence_column(event.target);
        },
        'kanban_record_update': 'update_record',
        'kanban_column_add_record': 'add_record_to_column',
        'kanban_column_delete': 'delete_column',
        'kanban_column_archive_records': 'archive_records',
        'column_add_record': 'column_add_record',
        'kanban_load_more': 'load_more',
        'kanban_call_method': 'call_method',
    },

    render_grouped: function (fragment) {
        var self = this;
        var record_options = _.extend(this.record_options, {
            draggable: false,
        });

        var column_options = this.get_column_options();

        _.each(this.data.groups, function (group) {
            var column = new FBKanbanColumn(self, group, column_options, record_options);
            column.appendTo(fragment);
            self.widgets.push(column);
        });
        this.postprocess_m2m_tags();
    },
    open_action: function (event) {
       
        var self = this;
        var node_context = event.data.context || {};
        var context = new data.CompoundContext(node_context);
        context.set_eval_context({
            active_id: event.target.id,
            active_ids: [event.target.id],
            active_model: this.dataset.model,
        });
        this.do_execute_action(event.data, this.dataset, event.target.id).then(function () {
            if(node_context['is_destroy']){
                event.target.destroy();
            }
            self.reload_record(event.target);
        });
    },
});

core.view_registry.add('fb_team_dashboard', FBDashboardView);

return FBDashboardView

});
