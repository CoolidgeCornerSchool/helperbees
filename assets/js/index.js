/* Javascript loaded for the index.html page */

$(document).ready(init_home);

const offers_url = API_BASE_URL + '/offer';

// All offers (includes many of the same offer_type)
var offers = null;

// enumerated distinct offer_types
var offer_types = {};

function init_home(){
    $.get(offers_url).done(on_load_offers);
    $('select#offer_type').change(choose_service);
    $('.jobs .col').click(choose_service);
    $('.section5 button').click(on_send_feedback);
}

function on_load_offers(data) {
    offers = data.result;
    // enumerate the distinct offer_types
    for (var i in offers) {
	offer = offers[i];
	offer_types[offer.offer_type] = true;
    }
    let dropdown = $('select#offer_type');

    // build dropdown menu from list of offer_types
    let ot_list = Object.keys(offer_types);
    ot_list.sort();
    for (var i in ot_list) {
	let offer_type = ot_list[i];
	let option = $('<option/>')
	    .attr('value', offer_type)
	    .text(offer_type);
	dropdown.append(option);
    }
}

// User clicked on service menu or clicked a big yellow button
function choose_service(){
    let val = $(this).val();           // value for drop-down menu
    let button_text = $(this).text();  // value for big yellow buttons
    if (val == '' && button_text != ''){
	val = button_text;
    }
    // navigate to new location
    window.location.href = '/request_helper#'+encodeURI(val).replace('/','<slash>');
}

// populate services menu with data from Google Sheet with known services types
function on_load_services(data) {
    // data is a tab-delimited table, one row per entry
    let dropdown = $('select#offer_type');
    let rows = data.split('\n');
    rows.shift(); // remove header
    rows.sort();
    for (var i in rows) {
	let row = rows[i];
	let cols = row.split('\t');
	let name = cols[0].trim('\r');
	let per_hour = cols[1].trim('\r');
	let unit = cols[2].trim('\r');
	let option = $('<option/>')
	    .attr({ value: name, per_hour: per_hour, unit: unit })
	    .text(name);
	dropdown.append(option);
    }
}

function on_send_feedback(){
    let msg_body = $('.section5 #body').val();
    let url = "mailto:ccs.helperbees@gmail.com?subject=feedback&body=" + encodeURI(msg_body);
    document.location.href=url;
    return false;
}
