---
---
$(document).ready(init_page);


var offers = null;
var offer_types = {};

const users_url = API_BASE_URL + '/user';

// This is how jQuery calls a function to initialize the page.
// It will be executed after all the html, css, and js for the page have been loaded.
function init_page() {
    // When logged in as admin, load all the data
    load_admin_data();

    // ADMIN_USERS tab
    // adds the ‘load_user’ callback to the names menu
    $('#names').change(load_user);

    // ADMIN_OFFERS tab
    $('select#offer_type').change(on_change_offer_type);
}

// When logged in as admin, load all the data
function load_admin_data(){
    with_admin_auth((headers)=>{
	// change displayed alert from 'not logged in' to 'logged in'
	$('.not-login-alert').addClass('d-none');
	$('.login-alert').removeClass('d-none');
	// get a list of all offers from the back end
	$.ajax({
	    dataType: 'json',
	    url: API_BASE_URL + '/offer',
	    headers: headers,
	    success: on_load_offers
	});
	// get a list of all users from the back end
	$.ajax({
	    dataType: "json",
	    url: users_url,
	    headers: headers,
	    success: on_load_users
	});
	// get a list of all orders from the back end	
	$.ajax({
	    dataType: "json",
	    url: API_BASE_URL + '/order',
	    headers: headers,
	    success: on_load_orders
	});
    });
}


function on_load_orders(data) {
    $('.no_orders').addClass('d-none');
    $('.admin_orders').removeClass('d-none');
    $('.admin_orders tbody').empty();
    for (var i in data.result){
	let order = data.result[i];
	$('.admin_orders').append(make_order_row(order));
    }
}


// returns <tr/>
function make_order_row(order){
    let row = $('<tr/>');
    row.append($('<td/>').text(new Date(order.payment_date).toLocaleString()));
    row.append($('<td/>').text(order.order_id));
    row.append($('<td/>').append(
	$('<span/>').text(order.first_name + ' ' + order.last_name).addClass('mr-2'),
	$('<a/>').text(order.payer_email).attr('href', 'mailto:'+ order.payer_email)));
    row.append($('<td/>').text('$'+order.payment_gross));
    let item_name = order.item_name;
    let match = /HelperBees \((.*)\)/.exec(item_name);
    if (match){
	name = match[1];
    } else {
	name = item_name;
    }
    row.append($('<td/>').text(name));
    return row;
}


// used when sorting, compares two objects (apply fcn to each object)
function compare( a, b, fcn ) {
    let fa = fcn(a);
    let fb = fcn(b);
    if ( fa < fb ){ return -1; }
    if ( fa > fb ){ return 1; }
    return 0;
}

// alphabetical by last_name
function compare_users( a, b ) {
    return compare(a, b, (user)=>user.last_name.toLowerCase());
}

// This is called when the list of all users arrives from the back end.
// It adds all the OPTION menu items to the names menu.
function on_load_users(data) {
    let users = data.result;
    users.sort(compare_users);
    for (var i in users) {
	let user = users[i];
	let name = user.first_name + ' ' + user.last_name;
	let option = $('<option/>')
	    .attr('value', user.user_id)
	    .text(name);
	$('#names').append(option);
    }
}

// This is called when the names menu changes (see init_page)
function load_user() {
    let user_id = $(this).val();
    if (typeof user_id != 'undefined') {
	let url = users_url + '/' + user_id;
	with_admin_auth((headers)=>{
	    $.ajax({dataType: "json",
		    url: url,
		    headers: headers,
		    success: on_load_user
		   });
	});
    }
}

// This is called when the data for one user arrives from the back end.
function on_load_user(data) {
    console.log('loaded', data);
    // By default, this table is invisible. Remove the d-none class to make it appear
    $('.show_user').removeClass('d-none');
    // Put data into the table
    let fields = ['first_name', 'last_name', 'parent_name', 'parent_email', 'parent_phone'];
    for (var i in fields){
	let field = fields[i];
	$('.show_user .'+field).text(data[field]);
    }
    let link_url = '{{ site.url }}/login#' + data.login_code;
    let link = $('<a/>').attr('href', link_url).text(link_url);
    let edit_link = $('<a/>').attr('href', 'edit_user#'+data.user_id).append('<i class="fa fa-edit"></i>');
    $('.show_user .login_link').html(link);
    $('.show_user .edit_link').html(edit_link);
    $('#delete_user').on('submit', function(e) {
	// delete_user(data);  // DISABLED until we have integrity: delete linked offers too
	e.preventDefault();
    });
}

function delete_user(data) {
    console.log('delete... ', data);
    //user_id = 'myuserid';
    user_id = data.user_id;
    url = users_url + '/' + user_id;
    console.log('url', url);
    
    with_admin_auth((headers)=>{
	$.ajax({
	    url: url,
	    headers: headers,
	    type: 'DELETE',
	    success: function(result) {
		success_msg = 'Kid deleted.';
		console.log(success_msg);
		show_alert({ result: 'success' });
	    },
	});
    });
}

function show_alert(result_struct) {
  $('.spinner').hide();
  $('.alert-box').show();
  var result = result_struct.result;
  if (result == 'success') {
    $('.alert-box .fail').hide();
    $('.alert-box .success').show();
  } else {
    $('.alert-box .success').hide();
    $('.alert-box .fail').show();
    $('.alert-box .fail .reason').html(result);
  }
  return false;
}

function on_load_offers(data) {
  offers = data.result;
  for (var i in offers) {
    offer = offers[i];
    offer_types[offer.offer_type] = true;
  }
  let dropdown = $('select#offer_type');
  let ot_list = Object.keys(offer_types);
  ot_list.sort();
  for (var i in ot_list) {
    let t = ot_list[i];
    let option = $('<option/>')
      .attr('value', t)
      .text(t);
    dropdown.append(option);
  }
}

function on_change_offer_type() {
    let type = $(this).val();
    let offerdivs = $('table.offers').empty();
    let header = $('<tr/>').append(
	$('<th/>').text('Item').css('width', '20%'),
	$('<th/>').text('Helper Bee').css('width', '20%'),
	$('<th/>').text('Description').css('width', '60%')
    );
    offerdivs.append(header);
    for (var i in offers) {
	let offer = offers[i];
	if (offer.offer_type == type) {
	    let helper_name = '';
	    if (typeof offer.user_first_name != 'undefined'){
		helper_name = offer.user_first_name + ' ' + offer.user_last_name;
	    }
	    let kid_cell = $('<td/>').append(helper_name);
	    let plural = '';
	    if (offer.offer_per_hour != 1){
		plural = 's';
	    }
	    let type_cell = $('<td/>').text(offer.offer_type +
					    ' (' + offer.offer_per_hour + ' ' + offer.offer_unit + plural + ') ');
	    let desc_cell = $('<td/>').text(offer.offer_description);
	    let offer_row = $('<tr/>')
		.append(type_cell, kid_cell, desc_cell)
		.addClass('align-items-center')
		.attr('offer_id', offer.offer_id)
		.attr('per_unit', offer.per_unit);
	    offerdivs.append(offer_row);
	}
    }
}
