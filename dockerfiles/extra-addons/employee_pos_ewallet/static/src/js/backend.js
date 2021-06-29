function openerp_backend(instance, module){
	var QWeb = instance.web.qweb;
    instance.web.list.Image = instance.web.list.Column.extend({
        format: function (row_data, options) {
            var self = this;
            self.display = self.display || 'inline';
            if (!row_data[self.id] || !row_data[self.id].value) {
                return '';
            }
            var value = row_data[self.id].value;
            if (self.type === 'binary') {
                if (value && value.substr(0, 10).indexOf(' ') === -1) {
                    self.src = "data:image/png;base64," + value;
                } else {
                    var imageArgs = {
                        model: options.model,
                        field: self.id,
                        id: options.id
                    }
                    if (self.resize) {
                        imageArgs.resize = self.resize;
                    }
                    self.src = instance.session.url('/web/binary/image', imageArgs);
                }
            } else {
                if (!/\//.test(row_data[self.id].value)) {
                    self.src = '/web/static/src/img/icons/' +
                               row_data[self.id].value + '.png';
                } else {
                    self.src = row_data[self.id].value;
                }
            }
            if (self.display == 'icon' || self.display == 'thumbnail'){
                var popupId = "o_web_tree_image_popup-" + row_data.id.value;
                var clickableId = "o_web_tree_image_clickable-" + row_data.id.value;
                if (!$('#' + popupId).length){
                    $("body").append(QWeb.render("ListView.row.image.imageData",
                                     {widget: self,
                                      popupId: popupId}));
                }
                window.setTimeout(function() {
                        $("#" + clickableId).click(function() {
                        $('#' + popupId).modal('show');
                        return false;
                    });
                }, 0);
            }
            return QWeb.render('ListView.row.image', {widget: self, clickableId: clickableId});
        },
    });
    instance.web.list.columns.add('field.image', 'instance.web.list.Image');
};