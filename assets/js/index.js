/* Javascript loaded for the signup.html page */

$(document).ready(init_shop);

const offers_url = '/dummy_offers.json';
var offers = null;
var offer_types = {};

function init_shop() {
  $.get(offers_url).done(on_load_offers);
  $('select#offer_type').change(on_change_offer_type);
}

function on_load_offers(data) {
  offers = data;
  for (var i in offers) {
    offer = offers[i];
    offer_types[offer.type] = true;
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
    $('<th/>').text('Team'),
  );
  offerdivs.append(header);
  for (var i in offers) {
    let offer = offers[i];
    if (offer.type == type) {
      let team_cell = $('<td/>');
      let members = offer.team.members;
      for (var j in members) {
        let member = members[j];
        if (j > 0) {
          team_cell.append(', ');
        }
        team_cell.append(
          member.first_name + ' ' + member.initial + ' (grade=' + member.grade + ')',
        );
      }
      let type_cell = $('<td/>').text(offer.type + ' (per ' + ' ' + offer.unit + ') ');
      let buy_btn = $('<td/>').append(
        $('<button/>')
          .addClass('btn btn-sm btn-primary')
          .text('Donate'),
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
