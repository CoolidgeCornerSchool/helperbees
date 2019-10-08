$(document).ready(init_page);

const API_BASE_URL = 'https://pxa9qyui26.execute-api.us-east-1.amazonaws.com/dev/'

function init_page(){
    let url = API_BASE_URL + 'user';
    $.getJSON(url, null, on_load_users);
    $('#names').change(load_user);
}

function on_load_users(data){
    for (var i in data){
	let user = data[i];
	let name = user.first_name + ' ' + user.last_name;
	let option = $('<option/>').attr('value', user.user_id).text(name);
	$('#names').append(option);
    }
}

function load_user(){
    let user_id = $(this).val();
    if (typeof user_id != 'undefined'){
	let url = API_BASE_URL + 'user/' + user_id;
	$.getJSON(url, null, on_load_user);
    }
}

function on_load_user(data){
    console.log('loaded', data);
    $('.show_user').removeClass('d-none');
    $('.show_user .first').text(data.first_name);
    $('.show_user .last').text(data.last_name);
    $('.show_user .color').text(data.color);
}
