function openerp_pos(instance, module){
	
	var module = instance.point_of_sale;
    var _t = instance.web._t;
    var QWeb = instance.web.qweb;
    
    var round_di = instance.web.round_decimals;
    var round_pr = instance.web.round_precision;

    instance.point_of_sale.ProductScreenWidget = instance.point_of_sale.ProductScreenWidget.extend({
        init: function() {
            this._super.apply(this, arguments);
        },
        start:function(){
            var self = this;

            self.product_list_widget = new instance.point_of_sale.ProductListWidget(this,{
                click_product_action: function(product){
                    if(product.to_weight && self.pos.config.iface_electronic_scale){
                        self.pos_widget.screen_selector.set_current_screen('scale',{product: product});
                    }else{
                        self.pos.get('selectedOrder').addProduct(product);
                    }
                },
                product_list: self.pos.db.get_product_by_category(0)
            });
            self.product_list_widget.replace(this.$('.placeholder-ProductListWidget'));

            this.product_categories_widget = new instance.point_of_sale.ProductCategoriesWidget(this,{
                product_list_widget: this.product_list_widget,
            });
            this.product_categories_widget.replace(this.$('.placeholder-ProductCategoriesWidget'));
            pos = self.pos;
            selectedOrder = self.pos.get('selectedOrder');

            $('#re_print_ticket').click(function(){
            	if(!selectedOrder.get_customer_name()){
            		alert('Please select user first !');
            	}else{
//            		self.pos_widget.screen_selector.show_popup('pos_ticket_popup');
            		re_print_dialog = new instance.web.Dialog(this, {
	                    title: "Print Receipt",
	                    size: 'medium',
	                    buttons: [
	                        {text: _t("Ok"), click: function() {
//	                        	var ticket_no = dialog.$el.find('#ticket_no').val() || false;
	                        	var ticket_no = re_print_dialog.$el.find("#ticket_no").val();
	            				var show_ticket = false;
	            				if(ticket_no){
	            					new instance.web.Model("pos.order").call("search_read",[[['pos_reference', 'ilike', ticket_no]]], {}, {'async': false}).then(
	                                function(order) {
	                                	if(order && order[0]){
	                                		if(order.length > 2){
	                                			return alert(_t("Order not found.!"));
	                                		}
	                                	}else{
	                                		return alert(_t("Order not found.!"));;
	                                	}
	                                	if(selectedOrder.get_user_mode() == 'staff'){
	                                		if(selectedOrder.get_facultyId() == order[0].employee_id[0]){
	                                			show_ticket = true;
	                                		}
	                                	}else if(selectedOrder.get_user_mode() == 'student'){
	                                		if(selectedOrder.get_studentId() == order[0].student_id[0]){
	                                			show_ticket = true;
	                                		}
	                                	}
	                                	if(show_ticket){
	                                		var no_of_receipt_print = self.pos.config.no_of_receipt_print;
	                                		var flag = false;
	            		                    if(no_of_receipt_print > order[0].receipt_count){
	            		                    	var dt = new Date(order[0].date_order + "GMT");
	            									var n = dt.toLocaleDateString();
	            				                    var crmon = self.addZero(dt.getMonth()+1);
	            				                    var crdate = self.addZero(dt.getDate());
	            				                    var cryear = dt.getFullYear();
	            				                    var crHour = self.addZero(dt.getHours());
	            				                    var crMinute = self.addZero(dt.getMinutes());
	            				                    var crSecond = self.addZero(dt.getSeconds());
	            			                    var date_order = cryear +'-'+ crmon +'-'+ crdate +' '+crHour +':'+ crMinute +':'+ crSecond;
	            			                    var date_only = cryear +'-'+ crmon +'-'+ crdate;
	            		                    	var expiration_period = self.pos.config.expiration_period || false;
	            		                    	var time_period = self.pos.config.time_period || false;
	            		                    	if(!expiration_period){
	            		                    		return alert(_t("Please Select Expiration Period.!"));
	            		                    	}
	            		                    	if(expiration_period && expiration_period == "days"){
	            		                    		var new_date = new moment(date_order, "YYYY-MM-DD").add(time_period, 'days').format('YYYY-MM-DD');
	            		                    		if(new moment().format('YYYY-MM-DD') < new_date){
	            		                    			flag = true;
	            		                    		}
	            		                    	}else{
	            		                    		var new_hours = new moment(date_order).add(time_period, 'hours').format('HH');
	            		                    		if(new moment().format('YYYY-MM-DD') == date_only){
	            		                    			if(new moment().format('hh') < new_hours){
	            			                    			flag = true;
	            			                    		}
	            		                    		}
	            		                    	}
	            		                    	if(flag){
	            		                    		re_print_dialog.$el.modal('hide');
	            		                    		var currentOrderLines = selectedOrder.get('orderLines');
	            		                            if(currentOrderLines.length > 0) {
	            		                            	selectedOrder.set_order_id('');
	            		                                for (i=0; i <= currentOrderLines.length + 1; i++) {
	            		                                    (currentOrderLines).each(_.bind( function(item) {
	            		                                        selectedOrder.removeOrderline(item);
	            		                                    }, this));
	            		                                }
	            		                                selectedOrder.set_client(null);
	            		                            }
	            		                    		if(order[0].lines && order[0].lines[0]){
	            	                        			selectedOrder.set_amount_paid(order[0].amount_paid);
	            	    			                    selectedOrder.set_amount_return(Math.abs(order[0].amount_return));
	            	    			                    selectedOrder.set_amount_tax(order[0].amount_tax);
	            	    			                    selectedOrder.set_amount_total(order[0].amount_total);
	            	    			                    selectedOrder.set_company_id(order[0].company_id[1]);
	            	    			                    selectedOrder.set_date_order(order[0].date_order);
//	            	    			                    selectedOrder.set_pos_reference(order[0].pos_reference);
	            	    			                    self.pos.get_order().set('name',order[0].pos_reference)
	            	    			                    selectedOrder.set_user_name(order[0].user_id && order[0].user_id[1]);
	            	    			                    var statement_ids = [];
	            	    			                    if (order[0].statement_ids) {
	            	    			                    	var cashregisters = self.pos.cashregisters;
	            	    			                    	new instance.web.Model("account.bank.statement.line").call("search_read", [[['id','in',order[0].statement_ids]]], {}, {'async':false})
	            	    			                    	.then(function(st_res) {
	            	                                            if (st_res) {
	            	                                        	    _.each(st_res, function(st_line) {
	            	                                        	    	var selected_register = _.find(cashregisters, function(cashregister){
	            	                                        	    		return cashregister.journal_id[0] == st_line.journal_id[0];
	            	                                        	    	});
	            	                                        	    	if(selected_register){
	            	                                        	    		selectedOrder.addPaymentline(selected_register);
	            	                                        	    		selectedOrder.selected_paymentline.set_amount(st_line.amount);
	            	                                        	    	}
	            	                                        	    });
	            	                                            }
	            	                                        });
	            	    			                    }
	            	    		                        new instance.web.Model("pos.order.line").call("search_read", [[['id','in',order[0].lines]]], {}, {'async':false}).then(
	            	    	                            function(lines) {
	            	    	                            	if(lines && lines[0]){
	            	    	                            		var is_prod = true;
	            	    	                            		lines.map(function(res){
	            	    		                                    var product = self.pos.db.get_product_by_id(Number(res.product_id[0]));
	            	    		                                    if(product){
	            	    		                                    	var line = new instance.point_of_sale.Orderline({}, {pos: self.pos, order: this, product: product});
	            		    		                                    line.set_discount(res.discount);
	            		    		                                    line.set_quantity(res.qty);
	            		    		                                    line.set_unit_price(res.price_unit)
	            		    		                                    selectedOrder.get('orderLines').add(line);
	            	    		                                    }else{
	            	    		                                    	is_prod = false;
	            	    		                                    }
	            	    	                            		});
	            	    	                            		if(is_prod){
	            	    	                            			selectedOrder.set_order_id(order[0].id);
	            		    	    			                    new instance.web.Model("pos.order").call('write',[order[0].id,{'receipt_count':order[0].receipt_count+=1}])
	            		    	    			                    .done(function(result){
	            		    	    			                    	if(result){
	            		    	    			                    		self.pos_widget.screen_selector.set_current_screen('receipt');
	            		    	    			                    	}
	            		    	    			                    });
	            	    	                            		}else{
	            	    	                            			return alert("Products not loaded in this pos session.");
	            	    	                            		}
	            	    	                            	}
	            	    	                            });
	            	                        		}
	            		                    	}else{
	            		                    		return alert("Ticket printing time expired.!");
	            		                    	}
	            		                    }else{
	            		                    	return alert("Receipt printing limit is over!");
	            		                    }
	                                	}else{
	                                		return alert("Please enter your ticket number.!");
	                                	}
	                                });
	            				}else{
	            					return alert("Please enter ticket no.");
	            				}
                            }},
	                        {text: _t("Cancel"), click: function() {
	                        	re_print_dialog.$el.modal('hide');
	                        }}
	                    ]
	                }).open();
                	$('.modal-dialog').addClass('dialogcustome')
	                re_print_dialog.$el.html(QWeb.render("re-print-ticket", self));
	                $(".close").hide();
	                re_print_dialog.$el.find("input#ticket_no").focus();
	                self.pos_widget.onscreen_keyboard.connect($("#ticket_no"));

	               /* if(self.pos.config.iface_vkeyboard && self.pos_widget.onscreen_keyboard){

                    }*/
            	}
            });

            $("#logout").click(function() {
            	$('#selected_user').html('');
        		$('#user_balance').html('');
        		$('#select_user').show();
        		$('#logout').hide();
        		pos.get('selectedOrder').set_customer_name(null);
                pos.get('selectedOrder').destroy();
            });
            $("#main_select_user").click(function() {
            	self.pos_widget.screen_selector.show_popup('select_user_popup');
            });
            $("#select_user").click(function() {
                selectedOrder = pos.get('selectedOrder');
                dialog = new instance.web.Dialog(this, {
                    title: "Select User",
                    size: 'medium',
                    buttons: [
                        {text: _t("Ok"), click: function() {
                        	var search_by = dialog.$el.find("#search_by").val();
                        	var user_barcode = dialog.$el.find("input#user_name_barcode").val();
                        	var select_user = $("#user").val();
                            if (user_barcode.length > 0) {
                            	var selecteduser = null
                            	if($("#user").val() == 'Student'){
                            		var match_students = self.pos.op_students;
                            		var students = [];
                                	if (search_by == 'AccountID') {
//                                		student_part = self.pos.db.get_partner_by_ean13(user_barcode);
                                		_.each(match_students, function(stud){
                                			if (stud.ean13 == user_barcode) {
                                				students.push(stud);
                                			}
    					                });
                                		selecteduser = students[0];
                                	} else {
                                          var stud_full_name = null
                                		_.each(match_students, function(stud){
                                            stud_full_name = stud.name + ' ' + stud.middle_name + ' ' + stud.last_name
                                			if (stud_full_name == user_barcode) {
                                				students.push(stud);
                                			}
    					                });
                                		selecteduser = students[0];
                                	}
                            	} else {
                            		var match_faculty = self.pos.hr_faculty;
                            		var faculties = [];
                                	if (search_by == 'AccountID') {
//                                		student_part = self.pos.db.get_partner_by_ean13(user_barcode);
                                		_.each(match_faculty, function(fac){
                                			if (fac.ean13 == user_barcode) {
                                				faculties.push(fac);
                                			}
    					                });
                                		selecteduser = faculties[0];
                                	} else {
                                		_.each(match_faculty, function(fac){
                                			if (fac.name == user_barcode) {
                                				faculties.push(fac);
                                			}
    					                });
                                		selecteduser = faculties[0];
                                	}
                            	}
                            	if(selecteduser == undefined || selecteduser == null){
                            		alert("User Not Exist..!")
                            		return;
                            	}
                            	dialog.$el.modal('hide');
                            	pin_dialog = new instance.web.Dialog(this, {
				                    title: "PIN for: " + selecteduser.name,
				                    size: 'medium',
				                    buttons: [
				                        {text: _t("Ok"), click: function() {
				                            var user_pin = pin_dialog.$el.find("input#user_pin").val();
				                            if(!selecteduser.pin || selecteduser.pin == ''){
				                               	alert("Please update your PIN from your profile.");
				                               	return
				                            }
				                            else if(user_pin.length != 4){
				                               	alert("Please enter 4 digit pin.");
				                               	return
				                            }
				                            else if (user_pin == selecteduser.pin) {
				                            	if(self.pos.config.iface_vkeyboard && self.pos_widget.onscreen_keyboard){
									  	              self.pos_widget.onscreen_keyboard.hide();
									  			}
				                            	if(self.pos.config.iface_vkeyboard && self.pos_widget.onscreen_keyboard){
					                                self.pos_widget.onscreen_keyboard.connect($('.searchbox input'));
					                            }
				                            	pin_dialog.$el.modal('hide');
				                            	if(select_user == 'Employee') {
				                            		new instance.web.Model("hr.employee").get_func("search_read")([['id', '=', selecteduser.id]]).pipe(
						                                    function(faclt_res) {
						                                    	if (faclt_res && faclt_res[0]) {
							                                    	if(faclt_res[0].available_balance > 0 ){
							                                    		selectedOrder.set_user_mode('staff');
					                                                    selectedOrder.set_customer_name(selecteduser);
					                                                    selectedOrder.set_user_balance(faclt_res[0].available_balance);
					                                                    selectedOrder.set_studentId(false);
					                                                    selectedOrder.set_facultyId(selecteduser.id);
					                                                    selectedOrder.set_client('');
					                                                    $('#select_user').hide();
					                                                    $('#logout').show();
					                                                    $('#selected_user').html('Welcome ' + selecteduser.name +' !')
					                                                    $('#user_balance').html('Your balance is ' + faclt_res[0].available_balance.toFixed(2))
					                                                } else {
					                                                    alert ('You have insufficient balance.. !');
					                                                    $('#selected_user').html('')
					                                                    $('#user_balance').html('')
					                                                }
						                                    	}
						                                    }
						                                );
				                            	}
				                            } else {
				                            	alert ('Invalid PIN !');
				                            }
                                        }},
				                        {text: _t("Cancel"), click: function() {
				                        	if(self.pos.config.iface_vkeyboard && self.pos_widget.onscreen_keyboard){
								  	              self.pos_widget.onscreen_keyboard.hide();
								  			}
				                        	if(self.pos.config.iface_vkeyboard && self.pos_widget.onscreen_keyboard){
				                                self.pos_widget.onscreen_keyboard.connect($('.searchbox input'));
				                            }
				                            pin_dialog.$el.modal('hide');
				                        }}
				                    ]
				                }).open();
                            	$('.modal-dialog').addClass('dialogcustome')
				                pin_dialog.$el.html(QWeb.render("pos-user-pin", self));
				                $(".close").hide();
				                pin_dialog.$el.find("input#user_pin").focus();
				                if(self.pos.config.iface_vkeyboard && self.pos_widget.onscreen_keyboard){
				  	              self.pos_widget.onscreen_keyboard.connect($("input#user_pin"));
				  			    }
                            }
                        }},
                        {text: _t("Cancel"), click: function() {
                        	if(self.pos.config.iface_vkeyboard && self.pos_widget.onscreen_keyboard){
				  	              self.pos_widget.onscreen_keyboard.hide();
				  			}
                        	if(self.pos.config.iface_vkeyboard && self.pos_widget.onscreen_keyboard){
                                self.pos_widget.onscreen_keyboard.connect($('.searchbox input'));
                            }
                            dialog.$el.modal('hide');
                        }}
                    ]
                }).open();
                $('.modal-dialog').addClass('dialogcustome')
                dialog.$el.html(QWeb.render("pos-select-user", self));
                $(".close").hide();
                $("#search_by").change(function() {
                	if($("#search_by").val() == 'AccountID'){
                		$("#user_label").html("Enter AccountID")
                	} else {
                		$("#user_label").html("Enter Name")
                	}
                });
                var user_list = [];
                _.each(self.pos.hr_faculty, function(faculty){
                	user_list.push(faculty.name);
                });
                $("#user").change(function() {
                	if($("#user").val() == 'Student'){
                		user_list = []
                        _.each(self.pos.op_students, function(stud){
                        	user_list.push(stud.name + ' ' + stud.middle_name + ' ' + stud.last_name);
                        });
                	} else {
                		user_list = []
                		_.each(self.pos.hr_faculty, function(faculty){
                        	user_list.push(faculty.name);
                        });
                	}
                });
                dialog.$el.on('keyup', "input#user_name_barcode", function () {
                	if (dialog.$el.find("#search_by").val() == 'Name') {
				        dialog.$el.find("input#user_name_barcode").autocomplete({
				            source: user_list
				        });
                	} else {
                		dialog.$el.find("input#user_name_barcode").autocomplete({
                            source: []
                        });
                	}
			    });
			    dialog.$el.find("input#user_name_barcode").keyup();
			    if(self.pos.config.iface_vkeyboard && self.pos_widget.onscreen_keyboard){
	              self.pos_widget.onscreen_keyboard.connect($("input#user_name_barcode"));
			    }
            });
        },
        addZero: function(value){
			if (value < 10) {
    			value = "0" + value;
    	    }
    	    return value;
    	},
    });

    var _super_orderline = instance.point_of_sale.Orderline.prototype;
    instance.point_of_sale.Orderline = instance.point_of_sale.Orderline.extend({
    	initialize: function(attr,options){
    		_super_orderline.initialize.call(this, attr, options);
			this.location_id = false;
    	},
    	set_location_id: function(location_id){
			this.location_id = location_id;
		},
		get_location_id: function(){
			return this.location_id;
		},
		export_as_JSON: function() {
            var lines = _super_orderline.export_as_JSON.call(this);
            var default_stock_location = this.pos.config.stock_location_id ? this.pos.config.stock_location_id[0] : false
            var new_val = {
                location_id: this.get_location_id() || default_stock_location,
            }
            $.extend(lines, new_val);
            return lines;
        },
        can_be_merged_with: function(orderline){
        	var res = _super_orderline.can_be_merged_with.call(this, orderline);
        	if(this.get_location_id() !== orderline.get_location_id()){
        		return false
        	}
        	return res
        },
    });

    instance.point_of_sale.Order = instance.point_of_sale.Order.extend({
        initialize: function(attributes){
        	var self = this;
            Backbone.Model.prototype.initialize.apply(this, arguments);
            this.pos = attributes.pos;
            var sequence_num = false;
            new instance.web.Model("pos.session").call("search_read",[[['id', '=', self.pos.pos_session.id]],['sequence_number']], {}, {'async': false}).then(
            function(session) {
            	if(session && session[0]){
            		sequence_num = session[0].sequence_number++;
            	}else{
            		sequence_num = self.pos.pos_session.sequence_number++;
            	}
            });
            this.sequence_number = sequence_num || this.pos.pos_session.sequence_number++;
            this.uid =     this.generateUniqueId();
            this.set({
                creationDate:   new Date(),
                orderLines:     new instance.point_of_sale.OrderlineCollection(),
                paymentLines:   new instance.point_of_sale.PaymentlineCollection(),
                name:           _t("Order ") + this.uid,
                client:         null,
                customer_name:  null,
                user_bal:       null,
                amount_paid:    null,
                amount_return:  null,
                amount_tax:     null,
                amount_total:   null,
                company_id:     null,
                date_order:     null,
                pos_reference:  null,
                user_mode:		null,
            });
            this.selected_orderline   = undefined;
            this.selected_paymentline = undefined;
            this.screen_data = {};  // see ScreenSelector
            this.receipt_type = 'receipt';  // 'receipt' || 'invoice'
            this.temporary = attributes.temporary || false;
            this.interfac = 'normal'
            this.studentId = null;
            this.facultyId = null;
            this.is_self_service = false;
            this.is_from_pos = true;
            return this;
        },
        set_customer_name: function(customer_name) {
            this.set('customer_name', customer_name);
        },
        get_customer_name: function(){
            return this.get('customer_name');
        },
        set_user_balance: function(user_bal) {
        	this.set('user_bal', user_bal);
        },
        get_user_balance: function() {
        	return this.get('user_bal');
        },
        set_interface: function(interfac) {
            this.interfac = interfac;
        },
        get_interface: function(){
            return this.interfac;
        },
        set_studentId: function(studentId) {
            this.studentId = studentId;
        },
        set_is_self_service:function(is_self_service){
        	this.is_self_service = is_self_service;
        },
        get_is_self_service:function(){
        	return this.is_self_service;
        },
        set_is_from_pos:function(is_from_pos){
        	this.is_from_pos = is_from_pos;
        },
        get_is_from_pos:function(){
        	return this.is_from_pos;
        },
        get_studentId: function(){
            return this.studentId;
        },
        set_facultyId: function(facultyId) {
            this.facultyId = facultyId;
        },
        get_facultyId: function(){
            return this.facultyId;
        },
        cart_product_qnty: function(product_id,flag){
	    	var self = this;
	    	var res = 0;
	    	var order = self.pos.get_order();
	    	var orderlines = order.get('orderLines').models;
	    	if (flag){
	    		_.each(orderlines, function(orderline){
					if(orderline.product.id == product_id){
						res += orderline.quantity
					}
	    		});
				return res;
	    	} else {
	    		_.each(orderlines, function(orderline){
					if(orderline.product.id == product_id && !orderline.selected){
						res += orderline.quantity
					}
	    		});
	    		return res;
	    	}
	    },
        addProduct: function(product, options){
        	var self = this;
            options = options || {};
            var attr = JSON.parse(JSON.stringify(product));
            attr.pos = this.pos;
            attr.order = this;

            var product_quaty = self.cart_product_qnty(product.id,true);
			if(self.pos.config.restrict_order && product.type != "service"){
	        	if(self.pos.config.prod_qty_limit){
	        		var remain = product.qty_available-self.pos.config.prod_qty_limit
	        		if(product_quaty >= remain){
	        			if(self.pos.config.custom_msg){
	        				alert(self.pos.config.custom_msg);
		        		} else{
		        			alert("Product Out of Stock");
		        		}
	    				return
		        	} 
	        	} 
        		if(product_quaty>=product.qty_available && !self.pos.config.prod_qty_limit){
	        		if(self.pos.config.custom_msg){
	        			alert(self.pos.config.custom_msg);
	        		} else{
	        			alert("Product Out of Stock");
	        		}
	    			return
	        	}
	        }
            selectedOrder = this.pos.get('selectedOrder');
            var line = new instance.point_of_sale.Orderline({}, {pos: this.pos, order: this, product: product});

            if(options.quantity !== undefined){
                line.set_quantity(options.quantity);
            }
            if(options.price !== undefined){
                line.set_unit_price(options.price);
            }
            if(options.discount !== undefined){
                line.set_discount(options.discount);
            }
            
            if (this.pos.config.interface == 'self') {
            	if(!selectedOrder.get_customer_name()){
            		alert ('Please select user first !');
                	return;
            	}
            	total = attr.price + selectedOrder.getTotalTaxIncluded();
            	if (total <= this.get_user_balance()) {
            		var last_orderline = this.getLastOrderline();
                    if( last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false){
                        last_orderline.merge(line);
                    }else{
                        this.get('orderLines').add(line);
                    }
                    this.selectLine(this.getLastOrderline());
            	} else {
            		alert ('Sorry you have insufficient balance.. !');
            		return;
            	}
            } else {
            	var last_orderline = this.getLastOrderline();
                if( last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false){
                    last_orderline.merge(line);
                }else{
                    this.get('orderLines').add(line);
                }
                this.selectLine(this.getLastOrderline());
            }
        },
        addPaymentline: function(cashregister) {
        	if(this.pos.config.interface == 'normal'){
        		var paymentLines = this.get('paymentLines');
                var newPaymentline = new instance.point_of_sale.Paymentline({},{cashregister:cashregister, pos:this.pos});
                if(cashregister.journal.type !== 'cash'){
                    newPaymentline.set_amount( Math.max((this.getDueLeft()),0) );
                }
                paymentLines.add(newPaymentline);
                this.selectPaymentline(newPaymentline);
        	}
        	if(this.pos.config.interface == 'self'){
        		var paymentLines = this.get('paymentLines');
                var newPaymentline = new instance.point_of_sale.Paymentline({},{cashregister:cashregister, pos:this.pos});
                newPaymentline.set_amount( Math.max((this.getDueLeft()),0) );
                paymentLines.add(newPaymentline);
                this.selectPaymentline(newPaymentline);
        	}
        },
        export_as_JSON: function() {
            var orderLines, paymentLines;
            orderLines = [];
            (this.get('orderLines')).each(_.bind( function(item) {
                return orderLines.push([0, 0, item.export_as_JSON()]);
            }, this));
            paymentLines = [];
            (this.get('paymentLines')).each(_.bind( function(item) {
                return paymentLines.push([0, 0, item.export_as_JSON()]);
            }, this));
            return {
                name: this.getName(),
                amount_paid: this.getPaidTotal(),
                amount_total: this.getTotalTaxIncluded(),
                amount_tax: this.getTax(),
                amount_return: this.getChange(),
                lines: orderLines,
                statement_ids: paymentLines,
                pos_session_id: this.pos.pos_session.id,
                partner_id: this.get_client() ? this.get_client().id : false,
                user_id: this.pos.cashier ? this.pos.cashier.id : this.pos.user.id,
                uid: this.uid,
                sequence_number: this.sequence_number,
//                interface: this.get_interface(),
                student_id: this.get_studentId(),
                faculty_id: this.get_facultyId(),
                is_self_service: this.get_is_self_service(),
                is_from_pos: this.get_is_from_pos(),
            };
        },
        set_order_id: function(order_id){
            this.set('order_id', order_id);
        },
        get_order_id: function(){
            return this.get('order_id');
        },
        set_user_mode: function(user_mode){
            this.set('user_mode', user_mode);
        },
        get_user_mode: function(){
            return this.get('user_mode');
        },
        set_amount_paid: function(amount_paid) {
            this.set('amount_paid', amount_paid);
        },
        get_amount_paid: function() {
            return this.get('amount_paid');
        },
        set_amount_return: function(amount_return) {
            this.set('amount_return', Math.abs(amount_return));
        },
        get_amount_return: function() {
            return this.get('amount_return');
        },
        set_amount_tax: function(amount_tax) {
            this.set('amount_tax', amount_tax);
        },
        get_amount_tax: function() {
            return this.get('amount_tax');
        },
        set_amount_total: function(amount_total) {
            this.set('amount_total', amount_total);
        },
        get_amount_total: function() {
            return this.get('amount_total');
        },
        set_company_id: function(company_id) {
            this.set('company_id', company_id);
        },
        get_company_id: function() {
            return this.get('company_id');
        },
        set_date_order: function(date_order) {
            this.set('date_order', date_order);
        },
        get_date_order: function() {
            return this.get('date_order');
        },
        set_pos_reference: function(pos_reference) {
            this.set('pos_reference', pos_reference)
        },
        get_pos_reference: function() {
            return this.get('pos_reference')
        },
        set_user_name: function(user_id) {
            this.set('user_id', user_id);
        },
        get_user_name: function() {
            return this.get('user_id');
        },
        set_journal: function(statement_ids) {
            this.set('statement_ids', statement_ids)
        },
        get_journal: function() {
            return this.get('statement_ids');
        },
    });

    instance.point_of_sale.OrderWidget = instance.point_of_sale.OrderWidget.extend({
    	set_value: function(val) {
        	var order = this.pos.get('selectedOrder');
        	if (this.editable && order.getSelectedLine()) {
                var mode = this.numpad_state.get('mode');
                if( mode === 'quantity'){
                	if(val == ''){
                		order.getSelectedLine().set_quantity('remove');
                	} else {
                		if(val == 0){
                    		return;
                    	}
                		order.getSelectedLine().set_quantity(val);
                	}
                    if (order.get_facultyId()) {
                    	if (order.getTotalTaxIncluded() > order.get_customer_name().available_balance){
                        	alert ('Sorry you have insufficient balance.. !');
                        	order.getSelectedLine().set_quantity(1);
                        	$("#qty_mode").trigger('click');
                        }
                    }
                    if (order.get_studentId()) {
                    	if (order.getTotalTaxIncluded() > order.get_customer_name().stud_balance_amount){
                        	alert ('Sorry you have insufficient balance.. !');
                        	order.getSelectedLine().set_quantity(1);
                        	$("#qty_mode").trigger('click')
                        }
                    }
                    
                }else if( mode === 'discount'){
                    order.getSelectedLine().set_discount(val);
                }else if( mode === 'price'){
                    order.getSelectedLine().set_unit_price(val);
                }
        	}
        },
    });
    
    instance.point_of_sale.PosModel = instance.point_of_sale.PosModel.extend({
        models: [
        {
            model:  'res.users',
            fields: ['name','company_id','partner_id'],
            ids:    function(self){ return [self.session.uid]; },
            loaded: function(self,users){ self.user = users[0]; },
        },{ 
            model:  'res.company',
            fields: [ 'currency_id', 'email', 'website', 'company_registry', 'vat', 'name', 'phone', 'partner_id' , 'country_id', 'tax_calculation_rounding_method'],
            ids:    function(self){ return [self.user.company_id[0]] },
            loaded: function(self,companies){ self.company = companies[0]; },
        },{
            model:  'decimal.precision',
            fields: ['name','digits'],
            loaded: function(self,dps){
                self.dp  = {};
                for (var i = 0; i < dps.length; i++) {
                    self.dp[dps[i].name] = dps[i].digits;
                }
            },
        },{ 
            model:  'product.uom',
            fields: [],
            domain: null,
            context: function(self){ return { active_test: false }; },
            loaded: function(self,units){
                self.units = units;
                var units_by_id = {};
                for(var i = 0, len = units.length; i < len; i++){
                    units_by_id[units[i].id] = units[i];
                    units[i].groupable = ( units[i].category_id[0] === 1 );
                    units[i].is_unit   = ( units[i].id === 1 );
                }
                self.units_by_id = units_by_id;
            }
        },{
            model:  'res.users',
            fields: ['name','ean13','partner_id'],
            domain: null,
            loaded: function(self,users){ self.users = users; },
        },{
            model:  'hr.employee',
            fields: ['name','ean13','pin'],
            domain: null,
            loaded: function(self,hr_faculty){ 
            	self.hr_faculty = hr_faculty;
            },
        },{
            model:  'res.partner',
            fields: ['pin', 'name','street','city','state_id','country_id','vat','phone','zip','mobile','email','ean13','write_date'],
            domain: [['customer','=',true]],
            loaded: function(self,partners){
                self.partners = partners;
                self.db.add_partners(partners);
            },
        },{
            model:  'res.country',
            fields: ['name'],
            loaded: function(self,countries){
                self.countries = countries;
                self.company.country = null;
                for (var i = 0; i < countries.length; i++) {
                    if (countries[i].id === self.company.country_id[0]){
                        self.company.country = countries[i];
                    }
                }
            },
        },{
            model:  'account.tax',
            fields: ['name','amount', 'price_include', 'include_base_amount', 'type', 'child_ids', 'child_depend', 'include_base_amount'],
            domain: null,
            loaded: function(self, taxes){
                self.taxes = taxes;
                self.taxes_by_id = {};
                _.each(taxes, function(tax){
                    self.taxes_by_id[tax.id] = tax;
                });
                _.each(self.taxes_by_id, function(tax) {
                    tax.child_taxes = {};
                    _.each(tax.child_ids, function(child_tax_id) {
                        tax.child_taxes[child_tax_id] = self.taxes_by_id[child_tax_id];
                    });
                });
            },
        },{
            model:  'pos.session',
            fields: ['id', 'journal_ids','name','user_id','config_id','start_at','stop_at','sequence_number','login_number'],
            domain: function(self){ return [['state','=','opened'],['user_id','=',self.session.uid]]; },
            loaded: function(self,pos_sessions){
                self.pos_session = pos_sessions[0]; 

                var orders = self.db.get_orders();
                for (var i = 0; i < orders.length; i++) {
                    self.pos_session.sequence_number = Math.max(self.pos_session.sequence_number, orders[i].data.sequence_number+1);
                }
            },
        },{
            model: 'pos.config',
            fields: [],
            domain: function(self){ return [['id','=', self.pos_session.config_id[0]]]; },
            loaded: function(self,configs){
                self.config = configs[0];
                self.config.use_proxy = self.config.iface_payment_terminal || 
                                        self.config.iface_electronic_scale ||
                                        self.config.iface_print_via_proxy  ||
                                        self.config.iface_scan_via_proxy   ||
                                        self.config.iface_cashdrawer;
                
                self.barcode_reader.add_barcode_patterns({
                    'product':  self.config.barcode_product,
                    'cashier':  self.config.barcode_cashier,
                    'client':   self.config.barcode_customer,
                    'weight':   self.config.barcode_weight,
                    'discount': self.config.barcode_discount,
                    'price':    self.config.barcode_price,
                });

                if (self.config.company_id[0] !== self.user.company_id[0]) {
                    throw new Error(_t("Error: The Point of Sale User must belong to the same company as the Point of Sale. You are probably trying to load the point of sale as an administrator in a multi-company setup, with the administrator account set to the wrong company."));
                }
            },
        },{
            model: 'stock.location',
            fields: [],
            ids:    function(self){ return [self.config.stock_location_id[0]]; },
            loaded: function(self, locations){ 
            	self.shop = locations[0];
            },
        },{
            model:  'product.pricelist',
            fields: ['currency_id'],
            ids:    function(self){ return [self.config.pricelist_id[0]]; },
            loaded: function(self, pricelists){ self.pricelist = pricelists[0]; },
        },{
            model: 'res.currency',
            fields: ['name','symbol','position','rounding','accuracy'],
            ids:    function(self){ return [self.pricelist.currency_id[0]]; },
            loaded: function(self, currencies){
                self.currency = currencies[0];
                if (self.currency.rounding > 0) {
                    self.currency.decimals = Math.ceil(Math.log(1.0 / self.currency.rounding) / Math.log(10));
                } else {
                    self.currency.decimals = 0;
                }

            },
        },{
            model: 'product.packaging',
            fields: ['ean','product_tmpl_id'],
            domain: null,
            loaded: function(self, packagings){ 
                self.db.add_packagings(packagings);
            },
        },{
            model:  'pos.category',
            fields: ['id','name','parent_id','child_id','image'],
            domain: function(self){
                if (self.shop.category_ids.length > 0) {
                    return [['id', 'child_of', self.shop.category_ids]];
                } else {
                    return null;
                }
            },
            loaded: function(self, categories){
                self.db.add_categories(categories);
            },
        },
        {
            model:  'product.product',
            fields: ['display_name', 'list_price','price','pos_categ_id', 'taxes_id', 'ean13', 'default_code', 
                     'to_weight', 'uom_id', 'uos_id', 'uos_coeff', 'mes_type', 'description_sale', 'description',
                     'product_tmpl_id','qty_available','type','write_date'],
            domain: function(self){ 
            	if(self.shop.category_ids && self.shop.category_ids.length > 0){
            		return [['sale_ok','=',true],['available_in_pos','=',true], ['pos_categ_id', 'child_of', self.shop.category_ids], ['qty_available','>',0]];
            	}else{
            		return [['sale_ok','=',true],['available_in_pos','=',true], ['qty_available','>',0]];
            	}
            },
            context: function(self){ 
            	return { pricelist: self.pricelist.id, display_default_code: false, location: self.config.stock_location_id[0]}; 
            },
            loaded: function(self, products){
                self.db.add_products(products);
            },
        },
        {
            model:  'account.bank.statement',
            fields: ['account_id','currency','journal_id','state','name','user_id','pos_session_id'],
            domain: function(self){ return [['state', '=', 'open'],['pos_session_id', '=', self.pos_session.id]]; },
            loaded: function(self, bankstatements, tmp){
                self.bankstatements = bankstatements;

                tmp.journals = [];
                _.each(bankstatements,function(statement){
                    tmp.journals.push(statement.journal_id[0]);
                });
            },
        },{
            model:  'account.journal',
            fields: [],
            domain: function(self,tmp){ return [['id','in',tmp.journals]]; },
            loaded: function(self, journals){
                self.journals = journals;

                // associate the bank statements with their journals. 
                var bankstatements = self.bankstatements;
                for(var i = 0, ilen = bankstatements.length; i < ilen; i++){
                    for(var j = 0, jlen = journals.length; j < jlen; j++){
                        if(bankstatements[i].journal_id[0] === journals[j].id){
                            bankstatements[i].journal = journals[j];
                        }
                    }
                }
                self.cashregisters = bankstatements;
            },
        },{
            label: 'fonts',
            loaded: function(self){
                var fonts_loaded = new $.Deferred();

                // Waiting for fonts to be loaded to prevent receipt printing
                // from printing empty receipt while loading Inconsolata
                // ( The font used for the receipt ) 
                waitForWebfonts(['Lato','Inconsolata'], function(){
                    fonts_loaded.resolve();
                });

                // The JS used to detect font loading is not 100% robust, so
                // do not wait more than 5sec
                setTimeout(function(){
                    fonts_loaded.resolve();
                },5000);

                return fonts_loaded;
            },
        },{
            label: 'pictures',
            loaded: function(self){
                self.company_logo = new Image();
                var  logo_loaded = new $.Deferred();
                self.company_logo.onload = function(){
                    var img = self.company_logo;
                    var ratio = 1;
                    var targetwidth = 300;
                    var maxheight = 150;
                    if( img.width !== targetwidth ){
                        ratio = targetwidth / img.width;
                    }
                    if( img.height * ratio > maxheight ){
                        ratio = maxheight / img.height;
                    }
                    var width  = Math.floor(img.width * ratio);
                    var height = Math.floor(img.height * ratio);
                    var c = document.createElement('canvas');
                        c.width  = width;
                        c.height = height
                    var ctx = c.getContext('2d');
                        ctx.drawImage(self.company_logo,0,0, width, height);

                    self.company_logo_base64 = c.toDataURL();
                    logo_loaded.resolve();
                };
                self.company_logo.onerror = function(){
                    logo_loaded.reject();
                };
                    self.company_logo.crossOrigin = "anonymous";
                self.company_logo.src = '/web/binary/company_logo' +'?_'+Math.random();

                return logo_loaded;
            },
        },
        ],
        _save_to_server: function (orders, options) {
            if (!orders || !orders.length) {
                var result = $.Deferred();
                result.resolve([]);
                return result;
            }
                
            options = options || {};

            var self = this;
            var timeout = typeof options.timeout === 'number' ? options.timeout : 7500 * orders.length;

            // we try to send the order. shadow prevents a spinner if it takes too long. (unless we are sending an invoice,
            // then we want to notify the user that we are waiting on something )
            var posOrderModel = new instance.web.Model('pos.order');
            return posOrderModel.call('create_from_ui',
                [_.map(orders, function (order) {
                    order.to_invoice = options.to_invoice || false;
                    return order;
                })],
                undefined,
                {
                    shadow: !options.to_invoice,
                    timeout: timeout
                }
            ).then(function (server_ids) {
            	_.each(orders, function(order) {
	        		var lines = order.data.lines;
	        		_.each(lines, function(line){
	        		    if(line[2].location_id === self.config.stock_location_id[0]){
                            var product_id = line[2].product_id;
                            var product_qty = line[2].qty;
                            var product = self.db.get_product_by_id(product_id);
                            var remain_qty = product.qty_available - product_qty;
                            product.qty_available = remain_qty;
                            self.pos_widget.product_screen.product_list_widget.product_cache.cache_node(product.id)
	        			}
	        		});
	        	});
                _.each(orders, function (order) {
                    self.db.remove_order(order.id);
                });
                return server_ids;
            }).fail(function (error, event){
                if(error.code === 200 ){    // Business Logic Error, not a connection problem
                    self.pos_widget.screen_selector.show_popup('error-traceback',{
                        message: error.data.message,
                        comment: error.data.debug
                    });
                }
                // prevent an error popup creation by the rpc failure
                // we want the failure to be silent as we send the orders in the background
                event.preventDefault();
                console.error('Failed to send orders:', orders);
            });
        },
    });
    
    instance.point_of_sale.ReceiptScreenWidget = instance.point_of_sale.ScreenWidget.extend({
    	template: 'ReceiptScreenWidget',

        show_numpad:     false,
        show_leftpane:   false,

        show: function(){
            this._super();
            var self = this;

            if (this.pos.config.interface !== 'self') {
            	var print_button = this.add_action_button({
	                label: _t('Print'),
	                icon: '/point_of_sale/static/src/img/icons/png48/printer.png',
	                click: function(){ self.print(); },
	            });
            }

            var finish_button = this.add_action_button({
                    label: _t('Next Order'),
                    icon: '/point_of_sale/static/src/img/icons/png48/go-next.png',
                    click: function() { self.finishOrder(); },
                });

            this.refresh();

            if (!this.pos.get('selectedOrder')._printed) {
                this.print();
            }
            
            finish_button.set_disabled(true);   
            setTimeout(function(){
                finish_button.set_disabled(false);
            }, 2000);
            
            if (this.pos.config.interface == 'self') {
            	setTimeout(function(){
                	self.finishOrder();
                }, 4000);
            }
        },
        print: function() {
            this.pos.get('selectedOrder')._printed = true;
            window.print();
        },
        refresh: function() {
            var order = this.pos.get('selectedOrder');
            $('.pos-receipt-container', this.$el).html(QWeb.render('PosTicket',{
                    widget:this,
                    order: order,
                    orderlines: order.get('orderLines').models,
                    paymentlines: order.get('paymentLines').models,
                }));
        },
        close: function(){
            this._super();
        },
    	finishOrder: function() {
    		$('#selected_user').html('');
    		$('#user_balance').html('');
    		$('#select_user').show();
    		$('#logout').hide();
    		this.pos.get('selectedOrder').set_customer_name(null);
            this.pos.get('selectedOrder').destroy();
        },
    });
    
    instance.point_of_sale.NumpadWidget = instance.point_of_sale.NumpadWidget.extend({
    	start: function() {
            this.state.bind('change:mode', this.changedMode, this);
            this.changedMode();
            this.$el.find('.numpad-backspace').click(_.bind(this.clickDeleteLastChar, this));
            this.$el.find('.numpad-minus').click(_.bind(this.clickSwitchSign, this));
            this.$el.find('.number-char').click(_.bind(this.clickAppendNewChar, this));
            this.$el.find('.mode-button').click(_.bind(this.clickChangeMode, this));
            this.$el.find('#valid').click(_.bind(this.clickValidate, this));
        },
        clickValidate: function() {
        	order = this.pos.get('selectedOrder');
        	self = this;
        	if(order.get('orderLines').length > 0){
        		if(confirm("Are you sure you want to place this order ?")){
        			_.each(this.pos.cashregisters,function(cashregister) {
    					if(cashregister.journal_id[0] == self.pos.config.self_journal_id[0]){
    						order.addPaymentline(cashregister);
    					}
            		});
            		order.set_interface('self')
                  	payment_screen_obj = new instance.point_of_sale.PaymentScreenWidget(this, {});
                  	payment_screen_obj.validate_order();
        		}
        	} else {
        		alert("Orderline is empty..!")
        	}
        },
    });
    
    instance.point_of_sale.PaymentScreenWidget = instance.point_of_sale.PaymentScreenWidget.extend({
    	validate_order: function(options) {
            var self = this;
            options = options || {};

            var currentOrder = this.pos.get('selectedOrder');

            var sequence_num = false;
            new instance.web.Model("pos.session").call("search_read",[[['id', '=', self.pos.pos_session.id]],['sequence_number']], {}, {'async': false}).then(
            function(session) {
            	if(session && session[0]){
            		sequence_num = session[0].sequence_number++;
            	}else{
            		sequence_num = self.pos.pos_session.sequence_number++;
            	}
            });
            if(sequence_num){
            	currentOrder.sequence_number = sequence_num;
            	currentOrder.uid = '';
            	currentOrder.uid = currentOrder.generateUniqueId();
            	currentOrder.set('name', _t("Order ") + currentOrder.uid);
            }
            currentOrder.set_is_self_service(true);
            if(currentOrder.get('orderLines').models.length === 0){
                this.pos_widget.screen_selector.show_popup('error',{
                    'message': _t('Empty Order'),
                    'comment': _t('There must be at least one product in your order before it can be validated'),
                });
                return;
            }

            var plines = currentOrder.get('paymentLines').models;
            for (var i = 0; i < plines.length; i++) {
                if (plines[i].get_type() === 'bank' && plines[i].get_amount() < 0) {
                    this.pos_widget.screen_selector.show_popup('error',{
                        'message': _t('Negative Bank Payment'),
                        'comment': _t('You cannot have a negative amount in a Bank payment. Use a cash payment method to return money to the customer.'),
                    });
                    return;
                }
            }

            if(!this.is_paid()){
                return;
            }

            // The exact amount must be paid if there is no cash payment method defined.
            if (Math.abs(currentOrder.getTotalTaxIncluded() - currentOrder.getPaidTotal()) > 0.00001) {
                var cash = false;
                for (var i = 0; i < this.pos.cashregisters.length; i++) {
                    cash = cash || (this.pos.cashregisters[i].journal.type === 'cash');
                }
                if (!cash) {
                    this.pos_widget.screen_selector.show_popup('error',{
                        message: _t('Cannot return change without a cash payment method'),
                        comment: _t('There is no cash payment method available in this point of sale to handle the change.\n\n Please pay the exact amount or add a cash payment method in the point of sale configuration'),
                    });
                    return;
                }
            }

            if (this.pos.config.iface_cashdrawer) {
                    this.pos.proxy.open_cashbox();
            }

            if(options.invoice){
                // deactivate the validation button while we try to send the order
                this.pos_widget.action_bar.set_button_disabled('validation',true);
                this.pos_widget.action_bar.set_button_disabled('invoice',true);

                var invoiced = this.pos.push_and_invoice_order(currentOrder);

                invoiced.fail(function(error){
                    if(error === 'error-no-client'){
                        self.pos_widget.screen_selector.show_popup('error',{
                            message: _t('An anonymous order cannot be invoiced'),
                            comment: _t('Please select a client for this order. This can be done by clicking the order tab'),
                        });
                    }else{
                        self.pos_widget.screen_selector.show_popup('error',{
                            message: _t('The order could not be sent'),
                            comment: _t('Check your internet connection and try again.'),
                        });
                    }
                    self.pos_widget.action_bar.set_button_disabled('validation',false);
                    self.pos_widget.action_bar.set_button_disabled('invoice',false);
                });

                invoiced.done(function(){
                    self.pos_widget.action_bar.set_button_disabled('validation',false);
                    self.pos_widget.action_bar.set_button_disabled('invoice',false);
                    self.pos.get('selectedOrder').set_customer_name(null);
                    self.pos.get('selectedOrder').destroy();
                });

            } else {
                this.pos.push_order(currentOrder) 
                if (this.pos.config.iface_print_via_proxy) {
                    var receipt = currentOrder.export_for_printing();
                    this.pos.proxy.print_receipt(QWeb.render('XmlReceipt',{
                        receipt: receipt, widget: self,
                    }));
                    this.pos.get('selectedOrder').set_customer_name(null);
                    this.pos.get('selectedOrder').destroy();    //finish order and go back to scan screen
                } else {
                	if (this.pos.config.interface == 'self') {
                		alert ("Your transaction was successful and your account has been debited. Thanks for your service");
                		var rem = Number(this.pos.get('selectedOrder').get_user_balance())-Number(this.pos.get('selectedOrder').getTotalTaxIncluded());
                		$('#user_balance').html('Your balance is '+rem);
                		this.pos_widget.screen_selector.set_current_screen(this.next_screen);
                	} else {
                		this.pos_widget.screen_selector.set_current_screen(this.next_screen);
                	}
                }
            }

            // hide onscreen (iOS) keyboard 
            setTimeout(function(){
                document.activeElement.blur();
                $("input").blur();
            },250);
        },
    });

    module.ProductQtyStructurePopupWidget = instance.point_of_sale.PopUpWidget.extend({
        template:'ProductQtyStructurePopupWidget',
        show: function(options){
            var self = this;
            self.prod_info_data = options.prod_info_data || false;
	        self.total_qty = options.total_qty || '';
	        self.product = options.product || false;
        	this._super();
            this.renderElement();
            this.$('.button.cancel').click(function(){
                self.pos_widget.screen_selector.close_popup();
            });
            this.$('.button.confirm').click(function(){
            	var order = self.pos.get_order();
    	        for(var i in self.prod_info_data){
    	        	var loc_id = self.prod_info_data[i][2]
    	        	if($("#"+loc_id).val() && Number($("#"+loc_id).val()) > 0){
    					order.addProduct(self.product,{quantity:$("#"+loc_id).val(),force_allow:true})
    					if(order.getSelectedLine()){
    						order.getSelectedLine().set_location_id(loc_id);
    					}
    	        	}
    	        }
                self.pos_widget.screen_selector.close_popup();
            });
        },
    });

    module.PosWidget.include({
    	build_widgets: function() {
            var self = this;
            this._super();
            this.prod_qty_popup = new module.ProductQtyStructurePopupWidget(this,{});
            this.prod_qty_popup.appendTo(this.$el);
            this.screen_selector.popup_set['prod_qty'] = this.prod_qty_popup;
            this.prod_qty_popup.hide();
    	},
    });

    instance.point_of_sale.ProductListWidget = instance.point_of_sale.ProductListWidget.extend({
    	init: function(parent, options) {
            var self = this;
            this._super(parent,options);
            this.click_product_handler = function(e){
                var product = self.pos.db.get_product_by_id(this.dataset.productId);
                if($(e.target).attr('class') === "product-qty-low" || $(e.target).attr('class') === "product-qty"){
                	var prod = product;
    	        	var prod_info = [];
                    var total_qty = 0;
                    var total_qty = 0;
                    new instance.web.Model('stock.warehouse').call('disp_prod_stock',[prod.id,self.pos.shop.id]).then(function(result){
	                    if(result){
	                    	prod_info = result[0];
	                        total_qty = result[1];
	                        self.pos_widget.screen_selector.show_popup('prod_qty', {prod_info_data:prod_info,total_qty: total_qty,product: product});
	                    }
    		    	}).fail(function (error, event){
    			        if(error.code === -32098) {
    			        	alert("Server Down...");
    			        	event.preventDefault();
    		           }
    		    	});
                }else{
                    options.click_product_action(product);
                }
            };
    	},
    });

    instance.point_of_sale.ProductCategoriesWidget = instance.point_of_sale.ProductCategoriesWidget.extend({
    	init: function(parent, options){
    		var self = this;
            this._super(parent,options);
            // Call function every 5 minutes
            setInterval(function() {
            	self.get_product_qty();
            }, 300000);
    	},
    	get_product_qty: function(){
    		var self = this;
    		var pricelist = self.pos.pricelist.id || false;
            var shop_id = self.pos.shop.id;
            var product_write_date = self.pos.db.get_product_write_date();
            $.ajax({
	            type: "POST",
	            url: '/web/dataset/get_products_qty',
	            data: {model: 'product.product',
	            		shop_id: shop_id,
	            		category_ids: JSON.stringify(self.pos.shop.category_ids),
	            		pricelist: pricelist,
	            		product_write_date:product_write_date,
                },
	            success: function(res) {
	                updated_products = JSON.parse(res);
	                updated_products = JSON.parse(res);
	                if(updated_products && updated_products[0]){
	                	self.pos.db.add_products(updated_products);
	                	updated_products.map(function(product){
	                		$("[data-product-id='"+product.id+"']").find('.product-qty').html(product.qty_available);
	                		$("[data-product-id='"+product.id+"']").find('.product-qty-low').html(product.qty_available);
	                	});
	                }
	            },
	            error: function() {
	                console.log('Qa-run failed.');
	                if($('#product_icon').hasClass('indicater_on')){
	                	$('#product_icon').addClass('indicater_off');
	                }
	            },
	        });
    	}
    });

    var _super_PosDB = instance.point_of_sale.PosDB.prototype;
    instance.point_of_sale.PosDB  = instance.point_of_sale.PosDB.extend({
        init: function(options){
        	this._super.apply(this, arguments);
        	var self = this;
        	self.product_write_date = null;
        },
        add_products: function(products){
        	var self = this;
        	_super_PosDB.add_products.call(this, products);
        	var new_write_date = '';
        	for(var i = 0, len = products.length; i < len; i++){
                var product = products[i];
                if (    this.product_write_date && 
                        this.product_by_id[product.id] &&
                        new Date(this.product_write_date).getTime() + 1000 >=
                        new Date(product.write_date).getTime() ) {
                    continue;
                } else if ( new_write_date < product.write_date ) { 
                    new_write_date  = product.write_date;
                }
        	}
        	this.product_write_date = new_write_date || this.product_write_date;
        },
        get_product_write_date: function(){
        	var self = this;
            return self.product_write_date || new moment().format('YYYY-MM-DD') + " 00:00:00";
        },
    });

}
