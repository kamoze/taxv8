openerp.employee_pos_ewallet = function(instance) {

    instance.employee_pos_ewallet = {};

    var module = instance.employee_pos_ewallet;

    openerp_pos(instance,module);

    openerp_backend(instance,module);
};