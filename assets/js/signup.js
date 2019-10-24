/* Javascript loaded for the signup.html page */

$(document).ready(init_signup);

const API_BASE_URL = 'https://pxa9qyui26.execute-api.us-east-1.amazonaws.com/dev/';

const service_types_url =
  'https://docs.google.com/spreadsheets/d/1kNrnfhhqY0vPJ4yB61eWEeyBtcqn-vCUHffBN2aOBUI/export?gid=0&format=tsv';

function init_signup() {
  $.get(service_types_url).done(on_load_service_types);
  $('form.signup select#offer_type').change(on_change_offer_type);
  $('form.signup input#offer_type_other').change(on_change_offer_type_other);
  $('form.signup').on('submit', function(e) {
    submit_data();
    e.preventDefault(); //prevent form from submitting
  });
}

function on_change_offer_type() {
  let val = $(this).val();
  let other = $('form.signup input#offer_type_other');
  var option = $('option:selected', this);
  $('#offer_units option').removeAttr('disabled');
  $('#offer_per_hour')
    .val('')
    .removeClass('form-control-plaintext');
  if (val == 'other') {
    other.removeClass('d-none');
    $('#offer_units').val(unit);
  }
  if (val != 'other') {
    other.val('').addClass('d-none');
    let unit = option.attr('unit');
    let per_hour = option.attr('per_hour');
    if (typeof unit != 'undefined') {
      $('#offer_units').val(unit);
      $('#offer_units option:not(:selected)').attr('disabled', true);
    }
    if (typeof per_hour != 'undefined') {
      console.log;
      $('#offer_per_hour').val(per_hour);
      $('#offer_per_hour').addClass('form-control-plaintext');
    }
  }
}

function on_change_offer_type_other() {
  let val = $(this).val();
  if (val != '') {
    $('form.signup select#offer_type').val('other');
  }
}

function on_load_service_types(data) {
  let dropdown = $('form.signup select#offer_type');
  let rows = data.split('\n');
  rows.reverse(); // Items are appending in reverse order
  rows.pop(); // remove header
  for (var i in rows) {
    let row = rows[i];
    let cols = row.split('\t');
    let name = cols[0].trim('\r');
    let per_hour = cols[1].trim('\r');
    let unit = cols[2].trim('\r');
    let option = $('<option/>')
      .attr({ value: name, per_hour: per_hour, unit: unit })
      .text(name);
    dropdown.find('.choose').after(option);
  }
}

function get_data() {
  let first_name = $('input#first_name').val();
  let last_name = $('input#last_name').val();
  let parent_name = $('input#parent_name').val();
  let parent_phone = $('input#parent_phone').val();
  let parent_email = $('input#parent_email').val();
  return {
    first_name: first_name,
    last_name: last_name,
    parent_name: parent_name,
    parent_phone: parent_phone,
    parent_email: parent_email,
  };
}

function submit_data() {
  url = API_BASE_URL + 'user';
  data = get_data();
  data.grade = '8';
  console.log('url', url);
  $.post(url, JSON.stringify(data))
    .done(function(dataOut, textStatus, xhr) {
      var status = xhr.status;
      console.log(status);
      console.log('dataOut: ' + dataOut);
      console.log('dataOut.user_id: ' + dataOut.user_id);
      statusCode = dataOut.user_id.statusCode;
      console.log('statusCode: ' + statusCode);
      body = dataOut.user_id.body;
      if (statusCode === undefined) {
        success_msg = 'Kid added with user id ' + dataOut.user_id;
        console.log(success_msg);
        show_alert({ result: 'success' });
      } else {
        error_msg = 'Unable to add student. Status: ' + body;
        show_alert({ result: error_msg });
      }
    })
    .fail(function(xhr, textStatus, errorThrown) {
      error_msg = 'Unable to add student.';
      console.log(error_msg);
      show_alert({ result: error_msg });
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
