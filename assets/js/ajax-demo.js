$(document).ready(init_page);

const API_BASE_URL = 'https://pxa9qyui26.execute-api.us-east-1.amazonaws.com/dev/'

// This is how jQuery calls a function to initialize the page.
// It will be executed after all the html, css, and js for the page have been loaded.
function init_page(){
    let url = API_BASE_URL + 'user';
    // get a list of all users from the back end
    $.getJSON(url, null, on_load_users);
    // adds the ‘load_user’ callback to the names menu (<SELECT/>)
    $('#names').change(load_user);
}

// This is called when the list of all users arrives from the back end.
// It adds all the OPTION menu items to the names menu.
function on_load_users(data){
    for (var i in data){
	let user = data[i];
	let name = user.first_name + ' ' + user.last_name;
	let option = $('<option/>').attr('value', user.user_id).text(name);
	$('#names').append(option);
    }
}

// This is called when the names menu changes (see init_page)
function load_user(){
    let user_id = $(this).val();
    if (typeof user_id != 'undefined'){
	let url = API_BASE_URL + 'user/' + user_id;
	$.getJSON(url, null, on_load_user);
    }
}

// This is called when the data for one user arrives from the back end.
function on_load_user(data){
    console.log('loaded', data);
    // By default, this table is invisible. Remove the d-none class to make it appear
    $('.show_user').removeClass('d-none');
    // Put data into the table
    $('.show_user .first').text(data.first_name);
    $('.show_user .last').text(data.last_name);
    $('.show_user .color').text(data.color);
}