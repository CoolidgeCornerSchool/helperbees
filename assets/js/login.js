/*
To log in, visit the login URL.
When a user (kid) account is created, they are issued a new login_code.
This code appears in a login URL emailed to the parent, and is also saved in a cookie in their browser.
As long as the browser has the cookie, USER_INFO should be populated with the user's details.

If the login URL is lost, you can request it to be sent again to the parent's email. (not yet implemented)
*/
$(document).ready(init_login);

const LOGIN_COOKIE = 'helperbee_login';
const LOGIN_DAYS = 30;

// If the user is logged in, it takes a few seconds for USER_INFO to load.
// You must write this as a callback. This will be called when USER_INFO gets loaded,
// then your function can do what it wants.
// 
// function my_function(user_info){
//     .. do something with user_info ..
// }
//
// USER_INFO.then(my_function);
//

const USER_INFO = $.Deferred();

function set_cookie(name, value, days = LOGIN_DAYS, path = '/') {
  const expires = new Date(Date.now() + days * 864e5).toUTCString()
    document.cookie = name + '=' + encodeURIComponent(value) + '; expires=' + expires + '; path=' + path + ';SameSite=Lax';
}

function get_cookie(name) {
  return document.cookie.split('; ').reduce((r, v) => {
    const parts = v.split('=')
    return parts[0] === name ? decodeURIComponent(parts[1]) : r
  }, '')
}

function delete_cookie(name, path = '/') {
  set_cookie(name, '', -1, path)
}

// If the user is logged in, save user details in USER_INFO.
function init_login(){
    console.log('init login');
    let path = window.location.pathname;
    let regex = /\/login\/(.*)$/;
    if (regex.test(path)){
	// New login: browser is visiting http://{HOST}/login/{login_code}
	new_code = regex.exec(path)[1];
	set_cookie(LOGIN_COOKIE, new_code);
	// Redirect to user page
	window.location.pathname = 'my_page';
    } else {
	// Browser is visiting http://{HOST}/login/{login_code}
	let old_code = get_cookie(LOGIN_COOKIE);
	if (old_code){
	    console.log('old cookie', old_code);
	    let url = API_BASE_URL + '/user/login/' + old_code;
	    $.get(url, on_login);
	}
    }
}

function on_login(data){
    console.log('logged in with', data);
    $('nav .tab-my_page').removeClass('d-none');
    USER_INFO.resolve(data);
}

