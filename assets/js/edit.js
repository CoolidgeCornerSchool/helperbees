
$(document).ready(init_edit);

const user_url = API_BASE_URL + '/user';

var is_admin = false;

function init_edit(){
    let path = window.location.pathname;
    let hash = window.location.hash;
    $('form.edit_user').submit(submit_user_data);
    user_id = hash.substr(1);
    if (user_id != ''){
	is_admin = true;
	with_admin_auth((headers)=>get_user(user_id, headers));
	return;
    }
    USER_INFO.then(on_load_user);
}


// get user info with authentication headers (either kid or admin)
function get_user(user_id, headers){
    let url = user_url + '/' + user_id;
    $.ajax({
	url: url,
	headers: headers,
	type: 'GET',
	success: on_load_user
    });
}

function on_load_user(data){
    for (var field in data){
	$('#'+field).val(data[field]);
    }
}

function submit_user_data(){
    let user_id = $('#user_id').val();
    if (user_id == ''){
	console.error('Missing user_id');
	return;
    }
    let params = $('form.edit_user').serialize();
    let data = params_to_object(new URLSearchParams(params));
    let url = user_url + '/' + user_id;
    if (is_admin){
	with_admin_auth((headers)=>update_user(url, headers, data));
    } else {
	with_user_auth((headers)=>update_user(url, headers, data));
    }
    return false;}

function update_user(url, headers, data){
    $.ajax({
	url: url,
	data: JSON.stringify(data),
	headers: headers,
	type: 'PUT'
    }).then(on_update_user);
}

function on_update_user(){
    window.history.back();
}

function params_to_object(entries) {
    let result = {}
    for(let entry of entries) { // each 'entry' is a [key, value] tuple
	const [key, value] = entry;
	result[key] = value;
    }
    return result;
}
