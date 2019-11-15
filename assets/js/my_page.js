---
---
$(document).ready(()=> {
    USER_INFO.then(init_about_me);
    $('button.logout').click(logout);
});


// If we're logged in, this will wait for USER_INFO to fetch the user's info.
// Then use it to fill in the form.
function init_about_me(user_info){
    // call get_orders with auth_heders and user_id.
    with_user_auth((headers)=>get_orders(headers, user_info.user_id));
    for (var field in user_info){
	let value = user_info[field];
	$('form#about_me #'+field).val(value);
    }
    let site_url = "{{ site.url }}";
    let link_url = site_url + '/login#' + user_info.login_code;
    let link = $('<a/>').attr('href', link_url).text(link_url);
    $('div#login_link').append(link);
    $('.logging-in').addClass('d-none');
    $('form#about_me').removeClass('d-none');
}

function get_orders(auth_headers, user_id){
    let offers_url = API_BASE_URL + '/offer';
    let orders_url = API_BASE_URL + '/order';
    $.ajax({
	url: offers_url,
	headers: headers,
	type: 'GET',
	success: (data)=>show_offers(data, user_id)
    });
    return;
    $.ajax({
	url: orders_url,
	headers: headers,
	type: 'GET',
	success: (data)=>show_orders(data, user_id)
    });    
}

function show_orders(data, user_id){
    console.log('show_orders', data);
    let exist = false;
    for (var i in data.result){
	let order = data.result[i];
	if (order.user_id != user_id){
	    continue;
	}
	console.log('order', order);
    }
}

function show_offers(data, user_id){
    let exist = false;
    $('.volunteered .items tbody').empty().append(
        $('<tr/>').append(
	    $('<th/>').text('Type'),
	    $('<th/>').text('Rate'),
	    $('<th/>').text('Description')));
    
    for (var i in data.result){
	let offer = data.result[i];
	if (offer.user_id != user_id){
	    continue;
	}
	exist = true;
	$('.volunteered .items tbody').append(make_offer_row(offer));
    }
    if (exist){
	$('.volunteered').removeClass('d-none');
    }
}

// returns a <tr/>
function make_offer_row(offer){
    console.log(offer);
    let type = offer.offer_type;
    if (type == 'other'){
	type += ': ' + offer.offer_type_other;
    }
    let rate = offer.offer_per_hour + ' ' + offer.offer_unit;
    if (offer.offer_per_hour > 1){
	rate += 's';
    }
    let row = $('<tr/>').append(
	$('<td/>').text(type),
	$('<td/>').text(rate),
	$('<td/>').text(offer.offer_description));
    return row;
}

    

function logout(){
    delete_cookie(LOGIN_COOKIE);
    window.location.pathname = '/';
    return false;
}
