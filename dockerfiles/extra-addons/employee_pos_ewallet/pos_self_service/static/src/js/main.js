openerp.pos_self_service = function(instance) {

    instance.pos_self_service = {};

    var module = instance.pos_self_service;

    openerp_pos(instance,module);

    openerp_backend(instance,module);
};