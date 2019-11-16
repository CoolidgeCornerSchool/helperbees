---
---
/* Javascript loaded for the volunteer.html page */

$(document).ready(init_signup);


// Google Sheet with known service types
const service_types_url = "{{ site.service_types_url }}";

function init_signup() {
    $('.spinner, .alert-box').hide();
    $.get(service_types_url).done(on_load_service_types);
    $('form.signup select#offer_type').change(on_change_offer_type);
    $('form.signup input#offer_type_other').change(on_change_offer_type_other);
    $('form.signup').submit(submit_form_data);
    $('form.signup button.signup').click(validate_offer_type);
    // USER_INFO is defined in login.js and resolves with kid's info if they are logged in.
    USER_INFO.then(populate_user_info);
}

// If a kid is logged in, prepopulate the form with their info and make it read-only.
function populate_user_info(user_info){
    let fields = ['first_name', 'last_name', 'parent_phone', 'parent_email', 'parent_name'];
    for (var i in fields){
	let field = fields[i];
	let input = $('form.signup input[name="'+field+'"]');
	input.val(user_info[field]).attr('readonly', true);
    }
}

function on_change_offer_type() {
    let val = $(this).val();
    let other = $('form.signup input#offer_type_other');
    var option = $('option:selected', this);
    $('#offer_unit option').removeAttr('disabled');
    $('#offer_per_hour').val('')
	.removeClass('form-control-plaintext');
    if (val == 'other') {
	other.removeClass('d-none');
	$('#10-for').text('$10 for');
	$('#10-for').addClass('col-1').removeClass('col');
	$('#offer_per_hour, #offer_unit').removeClass('d-none');
	$('#offer_per_hour').val(1);
    }
    if (val != 'other') {
	$('#10-for').removeClass('col-1').addClass('col');
	$('#offer_per_hour, #offer_unit').addClass('d-none').removeClass('d-inline-block');
	other.val('').addClass('d-none');
	let unit = option.attr('unit');
	let per_hour = option.attr('per_hour');
	let plural = '';
	if (per_hour > 1){
	    plural = 's';
	}
	$('#10-for').text('$10 for '+per_hour+ ' ' + unit + plural);
	if (typeof unit != 'undefined') {
	    $('#offer_unit').val(unit);
	}
	if (typeof per_hour != 'undefined') {
	    $('#offer_per_hour').val(per_hour);
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
    // data is a tab-delimited table, one row per entry
  let dropdown = $('form.signup select#offer_type');
  let rows = data.split('\n');
  rows.shift(); // remove header
  rows.sort();
  rows.reverse(); // Items are appended in reverse order
  for (var i in rows) {
    let row = rows[i];
    let cols = row.split('\t');
    let name = cols[0].trim('\r');
    let per_hour = cols[1].trim('\r');
    let unit = cols[2].trim('\r');
    let option = $('<option/>')
      .attr({ value: name, per_hour: per_hour, unit: unit })
      .text(name);
    dropdown.find('.hr').after(option);
  }
}

function get_data(){
    let params = $('form.signup').serialize();
    let data = params_to_object(new URLSearchParams(params));
    return data;
}

// Checks two fields: select#offer_type and input#offer_type_other.
// For each field, calls
//   setCustomValidity("")        # if valid or
//   setCustomValidity("message") # if not valid
function validate_offer_type(){
    offer_type = $('select#offer_type');
    offer_type_other = $('input#offer_type_other');
    if (offer_type.val() == 'choose'){
	offer_type[0].setCustomValidity("Choose the type of job");
    } else if (offer_type.val() == 'other' &&
	       (typeof offer_type_other.val() == 'undefined' || offer_type_other.val() == '')) {
	offer_type_other[0].setCustomValidity("Tell us what kind");
    } else {	
	offer_type[0].setCustomValidity("");
	offer_type_other[0].setCustomValidity("");
    }
}

function submit_form_data() {
    url = API_BASE_URL + '/offer_and_user';
    let params = $('form.signup').serialize();
    let data = params_to_object(new URLSearchParams(params));
    if (data.offer_type != 'other'){
	// don't include offer_type_other unless offer_type=='other'
	delete data.offer_type_other;
    }
    data.grade = '8';
    $.post(url, JSON.stringify(data)).then(say_thankyou);
    return false;
}

function say_thankyou(data, status, xhr){
    if (status == 'success'){
	// set cookie with login_code
	let new_code = data.login_code;
	if (typeof new_code != 'undefined'){
	    set_cookie(LOGIN_COOKIE, new_code);
	}
	// redirect to thankyou page
	window.location.href= '/volunteer_thankyou';
	return;
    }
    console.error("Error while handling form", data, status, xhr, xhr.status)
}

function params_to_object(entries) {
    let result = {}
    for(let entry of entries) { // each 'entry' is a [key, value] tuple
	const [key, value] = entry;
	result[key] = value;
    }
    return result;
}
