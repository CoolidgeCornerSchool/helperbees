$(document).ready(init_service_types);

const service_types_url = 'https://docs.google.com/spreadsheets/d/1kNrnfhhqY0vPJ4yB61eWEeyBtcqn-vCUHffBN2aOBUI/export?gid=0&format=tsv';

function init_service_types(){
    $.get(service_types_url).done(on_load_service_types);
}

function on_load_service_types(data){
    console.log(data);
    let dropdown = $('#services-dropdown');

    let rows = data.split('\n');
    for (var i in rows) {
	if (i == 0){
	    continue;  // skip table header
	};
	let row = rows[i]
	let cols = row.split('\t');
	console.log("row = ", cols);
	let option = $('<option/>').attr('value', cols[0]).text(cols[0]);
	dropdown.append(option);
    }
}
