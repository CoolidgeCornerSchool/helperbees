/* Javascript loaded for the signup.html page */

$(document).ready(init_signup);

const service_types_url = 'https://docs.google.com/spreadsheets/d/1kNrnfhhqY0vPJ4yB61eWEeyBtcqn-vCUHffBN2aOBUI/export?gid=0&format=tsv';

function init_signup(){
    $.get(service_types_url).done(on_load_service_types);
    $('form.signup select#offer_type').change(on_change_offer_type);
    $('form.signup input#offer_type_other').change(on_change_offer_type_other);
}

function on_change_offer_type(){
    let val = $(this).val();
    let other = $('form.signup input#offer_type_other');
    var option = $('option:selected', this);
    $('#offer_units option').removeAttr('disabled');
    $('#offer_per_hour').val('').removeClass('form-control-plaintext');
    if (val == 'other'){
	other.removeClass('d-none');
	$('#offer_units').val(unit);
    }
    if (val != 'other'){
	other.val('').addClass('d-none');
	let unit = option.attr('unit');
	let per_hour = option.attr('per_hour');
	if (typeof unit != 'undefined'){
	    $('#offer_units').val(unit);
	    $('#offer_units option:not(:selected)').attr('disabled', true);
	}
	if (typeof per_hour != 'undefined'){
	    console.log
	    $('#offer_per_hour').val(per_hour);
	    $('#offer_per_hour').addClass('form-control-plaintext');
	}
    }
}

function on_change_offer_type_other(){
    let val = $(this).val();
    if (val != ''){
	$('form.signup select#offer_type').val('other');
    }
}

function on_load_service_types(data){
    let dropdown = $('form.signup select#offer_type');
    let rows = data.split('\n');
    rows.reverse();   // Items are appending in reverse order
    rows.pop()        // remove header
    for (var i in rows) {
	let row = rows[i]
	let cols = row.split('\t');
	let name = cols[0].trim('\r');
	let per_hour = cols[1].trim('\r');
	let unit = cols[2].trim('\r');
	let option = $('<option/>')
	    .attr({value: name, per_hour: per_hour, unit: unit})
	    .text(name);
	dropdown.find('.choose').after(option);
    }
}
