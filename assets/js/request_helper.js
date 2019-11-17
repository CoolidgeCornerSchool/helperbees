---
---
/* Javascript loaded for the request_helper.html page */

$(document).ready(init_shop);

const offers_url = API_BASE_URL + '/offer';

const BASE_VALUE = 10; // default to $10

// This is a dedicated offer used for testing
const TEST_OFFER_ID = 'LB9LCi5Ahg4';

// All offers (includes many of the same offer_type)
var offers = null;

// enumerated distinct offer_types
var offer_types = {};

const test_offer = {
    offer_type: 'testing',
    offer_unit: 'item',
    offer_per_hour: 1,
    offer_description: 'Testing the payment and confirmation system'
};

function init_shop() {
    $.get(offers_url).done(on_load_offers);
    $('#extra_donation').change(on_change_donation);
    $('select#offer_type').change(on_change_offer_type);
}

function on_change_donation(){
    let input = $(this);
    let new_val = parseFloat(input.val());
    if (new_val < 0 || isNaN(new_val)){
	new_val = 0;
	$(input).val(new_val);
    }
    $('select#offer_type').change();
    return false;
}

// returns a <form/>
function paypal_button(offer_id, offer_type){
    let url = "https://www.paypal.com/cgi-bin/webscr"
    let form = $('<form/>').attr({action: url, method: "post", target:"_top"});
    let donation = parseFloat($('#extra_donation').val());
    if (isNaN(donation) || donation < 0){
	donation = 0;
    }
    let amount = BASE_VALUE + donation
    let fields = {
	business: "SLDPEE4HT6FHA", // merchant ID
	cmd: "_donations",
	amount: amount,
	item_name: "HelperBees (" + offer_type + ")",
	item_number: offer_id,
	custom: offer_id,
	shopping_url: "https://helperbees/request_helper",
	notify_url: "https://pxa9qyui26.execute-api.us-east-1.amazonaws.com/dev/order",
	image_url: "https://www.brookline.k12.ma.us/cms/lib/MA01907509/Centricity/Template/GlobalAssets/images/logos/devotion.jpg",
	return: "https://helperbees.org/request_thankyou"
    }
    let button_text = "Donate $10";
    if (donation != 0){
	if (Number.isInteger(donation)){
	    button_text = "Donate $" + amount;
	} else {
	    button_text = "Donate $" + amount.toFixed(2);
	}
    }
    let button_style = "btn-primary";
    if (offer_type == 'testing'){
	fields.amount = "0.01";
	button_text = "Test: $0.01";
	button_style = "btn-info";
    }

    form.append($('<button/>').attr("type","submit").addClass("btn").addClass(button_style).text(button_text));
    for (var name in fields){
	let input = $('<input/>').attr({type: "hidden", name: name, value: fields[name]});
	form.append(input);
    }
    return form;
}



function on_load_offers(data) {
    offers = data.result;
    // enumerate the distinct offer_types
    for (var i in offers) {
	offer = offers[i];
	offer_types[offer.offer_type] = true;
    }
    // use a known test offer
    test_offer.offer_id = TEST_OFFER_ID;
    offers.push(test_offer);    
    // If url has hashtag (e.g. #babysitting) select it in menu
    let path = window.location.pathname;
    let hash = decodeURI(window.location.hash).replace('<slash>', '/');
    let chosen = null;
    if (hash.length > 2 && path == '/request_helper'){
	chosen = hash.substr(1);
    }
    let dropdown = $('select#offer_type');

    // build dropdown menu from list of offer_types
    let ot_list = Object.keys(offer_types);
    ot_list.sort();
    ot_list.push('testing');
    for (var i in ot_list) {
	let offer_type = ot_list[i];
	let option = $('<option/>')
	    .attr('value', offer_type)
	    .text(offer_type);
	if (offer_type == chosen){
	    option.attr('selected', true);
	}
	dropdown.append(option);
    }
    dropdown.change();
}

// User makes choice from pull-down menu
function on_change_offer_type() {
    let offer_count = 0;
    let type = $(this).val();
    let offer_table = $('table.offers').empty();
    let header_row = $('<tr/>').append(
	$('<th/>').css('width', '20%'),
	$('<th/>').css('width', '60%').text('Description'),
	$('<th/>').css('width', '20%').text('Helper Bee'),
    );
    offer_table.append($('<thead/>').append(header_row));

    let tbody = $('<tbody/>');
    offer_table.append(tbody);
    for (var i in offers) {
	let offer = offers[i];
	if (offer.offer_type == type) {
	    let row = render_offer_row(offer);
	    tbody.append(row);
	    offer_count += 1;
	}
    }
    if (offer_count > 0){
	$('table.offers').removeClass('d-none');
    } else {
	$('table.offers').addClass('d-none');
    }	
}



// returns a row div
function render_offer_row(offer){
    let type_txt = offer.offer_type;
    if (type_txt == 'other' && offer.offer_type_other != '<empty>'){
	type_txt += ': ' + offer.offer_type_other;
    }
    let plural = '';
    if (offer.offer_per_hour != 1){
	plural = 's';
    }
    type_txt += ' (' + offer.offer_per_hour + ' ' + offer.offer_unit + plural + ') ';
    let type = $('<div/>').text(type_txt);
    let desc = $('<div/>').text(offer.offer_description);
    let about = $('<td/>').append(type, desc);
    let helper_name = '';
    if (typeof offer.user_first_name != 'undefined'){
	helper_name = offer.user_first_name + ' ' + offer.user_last_name;
    }
    let helper = $('<td/>').text(helper_name);
    let buy_btn = $('<td/>').append(paypal_button(offer.offer_id, offer.offer_type));
    return $('<tr/>')
        .append(buy_btn, about, helper)
        .addClass('align-items-center')
        .attr('offer_id', offer.offer_id);
}
