---
---
/* Javascript loaded for the request_helper.html page */

$(document).ready(init_shop);

const offers_url = API_BASE_URL + '/offer';
var offers = null;
var offer_types = {};

function init_shop() {
    $.get(offers_url).done(on_load_offers);
    $('select#offer_type').change(on_change_offer_type);
}

// TODO: Is it possible for /offer to return kid details so we don't need this?
function on_load_kids(data) {
  kidarray = data.result;
  for (var i in kidarray) {
    kidelement = kidarray[i];
    kids[kidelement.user_id] = kidelement;
  }
}

function on_load_offers(data) {
    offers = data.result;
    for (var i in offers) {
	offer = offers[i];
	offer_types[offer.offer_type] = true;
    }
    let path = window.location.pathname;
    let hash = decodeURI(window.location.hash).replace('<slash>', '/');
    let chosen = null;
    if (hash.length > 2 && path == '/request_helper'){
	chosen = hash.substr(1);
    }
    let dropdown = $('select#offer_type');
    let ot_list = Object.keys(offer_types);
    ot_list.sort();
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

function on_change_offer_type() {
    let offer_count = 0;
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
    console.log(offer);
    if (offer.offer_type == type) {
      let team_cell = $('<td/>');
	let kid = offer.user_id;
	
	//Kid information is redacted for now.
	//kid_details = kids[kid];
	//console.log(kid_details);
	//let last_initial = kid_details.last_name.substring(0, 1);
	//team_cell.append(kid_details.first_name + ' ' + last_initial);
	
      let type_cell = $('<td/>').text(
        offer.offer_type +
          ' (per ' +
          ' ' +
          offer.offer_unit +
          ', number of ' +
          offer.offer_unit +
          's: ' +
          offer.offer_per_hour +
          '): ' +
          offer.offer_description,
      );
      let buy_btn = $('<td/>').append(
        $('<button/>')
          .addClass('btn btn-sm btn-primary')
          .text('Donate $10'),
      );
      let offer_row = $('<tr/>')
        .append(buy_btn, type_cell, team_cell)
        .addClass('align-items-center')
        .attr('offer_id', offer.offer_id)
        .attr('per_unit', offer.per_unit);
	offerdivs.append(offer_row);
	offer_count += 1;
    }
  }
    if (offer_count > 0){
	$('table.offers').removeClass('d-none');
    } else {
	$('table.offers').addClass('d-none');
    }	
 
}
