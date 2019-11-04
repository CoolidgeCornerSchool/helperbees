---
---
/* Javascript loaded for the index.html page */

$(document).ready(init_home);

// Google Sheet with known service types
const service_types_url = "{{ site.service_types_url }}";

function init_home(){
    $.get(service_types_url).done(on_load_services);
    $('select#offer_type').change(choose_service);
}

// User clicked on service menu
function choose_service(){
    let val = $(this).val();
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



