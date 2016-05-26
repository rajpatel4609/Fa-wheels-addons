$(document).ready(function() {});

odoo.define('website.fawheels', function(require) {
    'use strict';
    $( "#product_new_search input" ).change(function(){
            var attrib_model =  '';
            var attrib_wheels = '';
            var attrib_products = '';
        var return_val =  function(vari, value){
            if (vari)return vari + "-" + value;
            return value;
        };
        $("input[name=attrib_model]").each(function(key, value){
            if($(value).prop("checked")){
                attrib_model = return_val(attrib_model,  $(value).val());
            }
        });
        $("input[name=attrib_wheels]").each(function(key, value){
            if($(value).prop("checked")){
                attrib_wheels = return_val(attrib_wheels,  $(value).val());
            }
        });
        $("input[name=attrib_products]").each(function(key, value){
            if($(value).prop("checked")){
                attrib_products = return_val(attrib_products,  $(value).val());
            }
        });
        window.location.href = $.query.set("attrib_model", attrib_model).set("attrib_wheels", attrib_wheels).set("attrib_products", attrib_products).toString();
    });

    var ajax = require('web.ajax');
    $("#brand_id").change(function() {
        var int_num = parseInt($("#brand_id option:selected").val());
        if (int_num) {
            ajax.jsonRpc('/fawheels/get_model', 'call', {
                'model_id': int_num,
            }).done(function(res) {
                $('#model_id option[value!="0"]').remove();
                _.each(res, function(ff) {
                        $('#model_id select').append($('<option>', {
                            value: ff["id"],
                            text: ff["name"]
                        }));
                });
            });
        }
    });

    $("#size_id").change(function() {
        var brand_id = parseInt($("#brand_id option:selected").val())
        var model_id = parseInt($("#model_id option:selected").val())
        var size_id = parseInt($("#size_id option:selected").val())

        window.location.href = $.query.set("domain_search", brand_id + "-" + model_id + "-" + size_id).toString()
    })
    $("#size_home_page").change(function() {
        var brand_id = parseInt($("#brand_id option:selected").val())
        var model_id = parseInt($("#model_id option:selected").val())
        var size_id = parseInt($("#size_home_page option:selected").val())
        ajax.jsonRpc('/fawheels/products', 'call', {
            'model_id': brand_id,
            'brand_id': model_id,
            'size_id': size_id,
        }).done(function(res) {
            console.log("yes yes yes", res)
        })
        window.location.href = "/shop" + $.query.set("domain_search", brand_id + "-" + model_id + "-" + size_id).toString()
    })
    $('.owl-carousel').owlCarousel({
        loop: true,
        margin: 30,
        responsiveClass: true,
        items: 4,
        loop: true,
        margin: 10,
        // autoplay:true,
        autoplayTimeout: 1000,
        autoplayHoverPause: true
    });
    $('#get-a-brief-quote').validate({
        rules: {
            email: {
                required: true,
                minlength: 5
            },
            confirm_email: {
                equalTo: '[name="email"]'
            },
            request_car_size: {
                required: true,
            },
        },
    });

    $("#datepicker").datepicker();

    $(".navbar-toggle").click(function() {
        $('body').toggleClass("menu-show");
    });

    $("#flexiselDemo2").flexisel({
        visibleItems: 1,
        animationSpeed: 1000,
        autoPlay: true,
        autoPlaySpeed: 8000,
        pauseOnHover: true,
        clone:true
    })

    // ------------Request a quick quote-----------------

        $("#request_car_size").change(function(){
            var request_size = $("#request_car_size").val();
            ajax.jsonRpc('/request_package_size', 'call', {
                    'size_id': parseInt(request_size),
            }).done(function(res){
                $('#request_product option[value!="0"]').remove();
                _.each(res, function(ff) {
                        $('#request_product').append($('<option>', {
                            value: ff["id"],
                            text: ff["name"]
                        }));
                });
            })
        });
        $("input#email_from").change(function() {
            var email_from_val = $("input#email_from").val();
            if (email_from_val) {
                ajax.jsonRpc('/is_callback_request', 'call', {
                    'email_id': email_from_val,
                }).done(function(res) {
                    if (res) {
                        alert('Request for quote from this email is already under process.')
                        $("input#cust_name").val(res['cust_name'])
                        if (res['cust_phone']) {
                            $("input#cust_phone").val(res['cust_phone'])
                        }

                    }
                })
            }
        });

    var clear_fields = function(email){
        if(!email){
            $("input[name=email]").val(" ")
        }
        $("input[name=city]").val(" ");
        $("input[name=country_id]").val(" ");
        $("input[name=house_number]").val(" ");
        $("input[name=postcode]").val(" ");
        $("input[name=street]").val(" ");
        $("input[name=street2]").val(" ");
        $("input[name=telephone]").val(" ");
        $("input[name=firstname]").val(" ");
        $("input[name=lastname]").val(" ");
        $("input[name=phone]").val(" ");
    }

    clear_fields();

    $("select[name='car_wheel_size']").change(function() {
        var car_wheel_size = $("select[name='car_wheel_size']").val();
        ajax.jsonRpc('/fawheels/fetch_get_products', 'call', {
            'wheel_size': car_wheel_size,
        }).done(function(res) {
            $("select[name='products'] option[value!='0']").remove();
            _.each(res, function(ff) {
                    $("select[name='products']").append($('<option>', {
                        value: ff["id"],
                        text: ff["name"]
                    }));
            });
        });
    });


    $("#car_brand").change(function() {
        var int_num = parseInt($("#car_brand option:selected").val());
        if (int_num) {
            ajax.jsonRpc('/fawheels/get_model', 'call', {
                'model_id': int_num,
            }).done(function(res) {
                $('#car_model option[value!="0"]').remove();
                _.each(res, function(ff) {
                        $('#car_model').append($('<option>', {
                            value: ff["id"],
                            text: ff["name"]
                        }));
                });
            });
        }
    });
    $("#search_postcode").change(function() {
        var postcode_value = $("#search_postcode").val();
        $("#postcode").val(postcode_value);
        if(postcode_value){
            ajax.jsonRpc('/fawheels/postcode', 'call', {
                'postcode': postcode_value,
            }).done(function(res) {
                    if(res['zip']){
                        $("input[name=postcode]").val(res['postcode']);
                    }
                    if(res['street']){
                        $("input[name=street]").val(res['street']);
                    }
                    if(res['city']){
                        $("input[name=city]").val(res['city']);
                    }
            });
        }
    });


    $("input[name=email]").change(function($e){
        if(! $($e.currentTarget).val()) return;
        if (confirm("Confirm Email Address : " + $($e.currentTarget).val()))
        {
           ajax.jsonRpc('/fawheels/get/partner', 'call', {
                'email': $($e.currentTarget).val(),
            }).done(function(res) {
                if (res.length){
                    res = res[0]
                    if(res['city']){
                        $("input[name=city]").val(res['city']);
                    }
                    if(res['country_id']){
                        $("input[name=country_id]").val(res['country_id']);
                    }
                    if(res['house_number']){
                        $("input[name=house_number]").val(res['house_number']);
                    }
                    if(res['postcode']){
                        $("input[name=postcode]").val(res['postcode']);
                    }
                    if(res['street']){
                        $("input[name=street]").val(res['street']);
                    }
                    if(res['street2']){
                        $("input[name=street2]").val(res['street2']);
                    }
                    if(res['mobile']){
                        $("input[name=telephone]").val(res['mobile']);
                    }
                    if(res['name']){
                        $("input[name=firstname]").val(res['name']);
                    }
                }else{
                    clear_fields(true);
                }
            });
        }else{
            clear_fields();
        }
    });
});
