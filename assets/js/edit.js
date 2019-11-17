
$(document).ready(init_edit);

const user_url = API_BASE_URL + '/user';
const offer_url = API_BASE_URL + '/offer';

var is_admin = false;

function init_edit(){
    let path = window.location.pathname;
    let hash = window.location.hash;
    $('form.edit_user').submit(()=>{
	user_id = $('#user_id').val();
	submit_form_data(user_id, user_url);
	return false;
    });
    $('form.edit_offer').submit(()=>{
	offer_id = $('#offer_id').val();
	submit_form_data(offer_id, offer_url);
	return false;
    });
    hash_id = hash.substr(1);
    if (hash_id != ''){
	// browser is visiting "/edit_xxx#yyy". See if admin is logged in, then get user info
	if (path == "/edit_user"){
	    user_id = hash_id;
	    is_admin = true;
	    with_admin_auth((headers)=>get_user(user_id, headers));
	    return;
	}
	if (path == "/edit_offer"){
	    offer_id = hash_id;
	    // could be logged in as user or admin, or both!
	    login_and_get_offer(offer_id);
	    return;
	}
    }
    if (path == "/edit_user"){
	// browser is visiting "/edit_user",
	// no hash, so see if user is logged in then get user info
	USER_INFO.then(on_load_user);
    }
}

// could be logged in as user or admin, or both!
// Use admin credentials if admin, else try user credentials.
// if not logged in, wait a second and try again (but give up after 8 tries)
function login_and_get_offer(offer_id, count=0){
    let max_tries = 8;     // stop after 8 tries
    let delay_msec = 1000; // wait 1 sec between tries
    let user = USER_INFO.state()       // when "resolved", means you're logged in as user
    let admin = GOOGLE_PROFILE.state() // when "resolved", means you're logged in as admin
    if (admin == 'resolved'){
	is_admin = true;
	with_admin_auth((headers)=>get_offer(offer_id, headers));
	return;
    } else if (user == 'resolved'){
	with_user_auth((headers)=>get_offer(offer_id, headers));
	return;
    }
    if (count > 8){
	console.error('Could not log in');
	return;
    }
    function retry() {login_and_get_offer(offer_id, count+1)}
    // sleep for 1 second and try it again
    setTimeout(retry, delay_msec);
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

// get offer info with authentication headers (either kid or admin)
function get_offer(offer_id, headers){
    let url = offer_url + '/' + offer_id;
    $.ajax({
	url: url,
	headers: headers,
	type: 'GET',
	success: on_load_offer
    });
}

function on_load_offer(data){
    for (var field in data){
	$('#'+field).val(data[field]);
    }
    $('#display_name').text(data.user_first_name + ' ' + data.user_last_name);
    $('#display_type').text(data.offer_type);
    if (data.offer_type == 'other'){
	// if type="other", display <input/> to specify "other"
	$('#offer_type_other').removeClass('d-none').addClass('d-inline-block');
	$('#offer_per').removeClass('d-none');
    } else {
	// if not "other", remove <input/> completely, so it won't be part of the submit()
	$('#offer_type_other').remove()
	// fix input
	$('#10-for').text('$10 for ' + data.offer_per_hour + ' ' + data.offer_unit)
	    .removeClass('col-1').addClass('col-4');
	// remove unused inputs
	$('#offer_per').remove();
    }
}

function on_load_user(data){
    for (var field in data){
	$('#'+field).val(data[field]);
    }
}

function submit_form_data(item_id, base_url){
    if (item_id == ''){
	console.error('Missing id');
	return;
    }
    let params = $('form').serialize();
    let data = params_to_object(new URLSearchParams(params));
    let url = base_url + '/' + item_id;
    let admin = GOOGLE_PROFILE.state() // when "resolved", means you're logged in as admin
    if (admin == 'resolved'){ // give priority to admin credentials, if you have them.
	is_admin = true;
    }
    if (is_admin){
	with_admin_auth((headers)=>update_item(url, headers, data));
    } else {
	with_user_auth((headers)=>update_item(url, headers, data));
    }
    return false;
}

function update_item(url, headers, data){
    $.ajax({
	url: url,
	data: JSON.stringify(data),
	headers: headers,
	type: 'PUT'
    }).then(on_update_item);
}

function on_update_item(){
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
