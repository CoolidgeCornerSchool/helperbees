---
---
/* Javascript loaded for the index.html page */

$(document).ready(init_home);

// Google Sheet with known service types
const service_types_url = "{{ site.service_types_url }}";

function init_home(){
    $.get(service_types_url).done(on_load_services);
    $('select#offer_type').change(choose_service);
    $('.jobs .col').click(choose_service);
    $('.section5 button').click(on_send_feedback);
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

