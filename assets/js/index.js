/* Javascript loaded for the signup.html page */

$(document).ready(init_shop);

const offers_url = 'https://pxa9qyui26.execute-api.us-east-1.amazonaws.com/dev/offer';
var offers = null;
var offer_types = {};

function init_shop() {
  $.get(offers_url).done(on_load_offers);
  $('select#offer_type').change(on_change_offer_type);
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
    console.log(offer);
    if (offer.offer_type == type) {
      let team_cell = $('<td/>');
      let kid = offer.user_id;
      team_cell.append(kid);
      let type_cell = $('<td/>').text(
        offer.offer_type +
          ' (per ' +
          ' ' +
          offer.offer_units +
          ', number of ' +
          offer.offer_units +
          's: ' +
          offer.offer_per_hour +
          ') ',
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
    }
  }
}
