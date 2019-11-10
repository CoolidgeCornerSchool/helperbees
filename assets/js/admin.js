---
---
$(document).ready(init_page);


var offers = null;
var offer_types = {};

// This is how jQuery calls a function to initialize the page.
// It will be executed after all the html, css, and js for the page have been loaded.
function init_page() {
    $('.spinner, .alert-box').hide();

    // When logged in as admin, load all the data
    load_admin_data();

    // ADMIN_USERS tab
    // adds the ‘load_user’ callback to the names menu
    $('#names').change(load_user);

    // ADMIN_OFFERS tab (login not required to view data)
    $.get(API_BASE_URL + '/offer').done(on_load_offers);
    $('select#offer_type').change(on_change_offer_type);

    // ADMIN_OFFERS tab
}

// When logged in as admin, load all the data
function load_admin_data(){
    with_admin_auth((headers)=>{
	// change displayed alert from 'not logged in' to 'logged in'
	$('.not-login-alert').addClass('d-none');
	$('.login-alert').removeClass('d-none');
	// get a list of all users from the back end
	$.ajax({
	    dataType: "json",
	    url: API_BASE_URL + '/user',
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


// returns <div/>
function make_order_row(order){
    let row = $('<tr/>');
    row.append($('<td/>').text(new Date(order.payment_date).toLocaleString()));
    row.append($('<td/>').text(order.order_id));
    row.append($('<td/>').append($('<a/>').text(order.first_name + ' ' + order.last_name)
				 .attr('href', 'mailto:'+ order.payer_email)));
    row.append($('<td/>').text('$'+order.payment_gross));
    
    return row;
}


// This is called when the list of all users arrives from the back end.
// It adds all the OPTION menu items to the names menu.
function on_load_users(data) {
    for (var i in data.result) {
	let user = data.result[i];
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
  $('.show_user .first').text(data.first_name);
  $('.show_user .last').text(data.last_name);
  // TODO: Remove all these '' once these parent fields are required.
  $('.show_user .parent_name').text('');
  $('.show_user .parent_name').text(data.parent_name);
  $('.show_user .parent_email').text('');
  $('.show_user .parent_email').text(data.parent_email);
  $('.show_user .parent_phone').text('');
  $('.show_user .parent_phone').text(data.parent_phone);
    

  let link_url = '{{ site.url }}/login#' + data.login_code;
  let link = $('<a/>').attr('href', link_url).text(link_url);
  $('.show_user .login_link').html(link);
  $('#delete_user').on('submit', function(e) {
    delete_user(data);
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
    $('<th/>'),
    $('<th/>').text('Description'),
    $('<th/>').text('Helper Bee'),
  );
  offerdivs.append(header);
  for (var i in offers) {
    let offer = offers[i];
    if (offer.offer_type == type) {
      let team_cell = $('<td/>');
      let kid = offer.user_id;
      team_cell.append(kid);
      let type_cell = $('<td/>').text(offer.offer_type + ' (per ' + ' ' + offer.offer_unit + ') ');
      let buy_btn = $('<td/>').append(
        $('<button/>')
          .addClass('btn btn-sm btn-primary')
          // Delete button
          .text('FIXME'),
      );
      let offer_row = $('<tr/>')
        .append(buy_btn, type_cell, team_cell)
        .addClass('align-items-center')
        .attr('offer_id', offer.offer_id)
        .attr('per_unit', offer.per_unit);
      offerdivs.append(offer_row);
    }
  }
}
