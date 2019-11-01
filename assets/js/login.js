---
---
/*

There are two totally unrelated ways to log in.
1: Login as a kid (simple, doesn't require the hassle of managing and resetting passwords)
2: Login as an admin (secure, requires a Google account)


*** Part 1: logging in as a kid ***

Kid logins are authenticated with a login_code (a short random string).
This is stored in the database for each user.
It's presented in a login url, and saved as a cookie.
No google code is used for this part.

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
// then your function can do what it wants. For an example, see print_user_info below.
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
    let path = window.location.pathname;
    let hash = window.location.hash;
    if (path == '/login' && hash == "#admin"){
	$('.admin').removeClass('d-none');
	return false;
    } else if (path == '/login' && hash.length > 2){
	// New login: browser is visiting http://{HOST}/login/#{login_code}
	new_code = hash.substr(1);
	set_cookie(LOGIN_COOKIE, new_code);
	// Redirect to user page
	window.location.pathname = 'my_page';
    } else {
	// Browser is visiting http://{HOST}/login#{login_code}
	let old_code = get_cookie(LOGIN_COOKIE);
	if (old_code){
	    let url = API_BASE_URL + '/user/login/' + old_code;
	    $.get(url, on_login);
	}
    }
}

// When user is logged in, this callback handles the user's info sent back from the /user/login API.
function on_login(data){
    $('nav .tab-my_page').removeClass('d-none');
    USER_INFO.resolve(data);
}

function print_user_info(user){
    console.log('logged in as', user.first_name, user.last_name, '<'+user.parent_email+'>');
}

// Print info in the console.
USER_INFO.then(print_user_info);

/* ---------------------------------------------------------------------------------------------------------
 *** Part 2: Logging in as an Admin  ***

When setting this up for a new project, you'll need to create new Google web sign-in credentials.
This is a OAuth 2.0 client ID with default scope (email and profile is all we need).

There's a second set of credentials for sending email. See install/setup_credentials/readme.md.
The send-email credentials are not the same as the admin-login credentials.
They have different scopes: sending email is much more sensitive, and is only set up for exactly
one user.

1. To configure admin-login, visit https://developers.google.com/identity/sign-in/web/sign-in 
2. Click 'configure a project' and proceed according to directions on that page.
   You will be creating a second project (separate from the send-email project).
3. Configure your project: calling from "web browser"
4. Add your web site urls to 'Authorized javascript origins'. Don't forget to hit 'save'.
5. Set the value of 'login_client_id' in '_config.yml' with the client-id for admin-login.

 */

const login_client_id = "{{ site.login_client_id }}";

// Displayed only on /login#admin page
// Executed after clicking the signin button
function on_google_signin(googleUser) {
    $('button.sign_out').removeClass('disabled btn-outline-primary').addClass('btn-primary');
    var profile = googleUser.getBasicProfile();
    console.log('ID: ' + profile.getId()); // Do not send to your backend! Use an ID token instead.
    console.log('Name: ' + profile.getName());
    console.log('Image URL: ' + profile.getImageUrl());
    console.log('Email: ' + profile.getEmail()); // This is null if the 'email' scope is not present.
    $('.avatar, .username').removeClass('d-none');
    $('.avatar').css('background-image', 'url(' + profile.getImageUrl() + ')')
    $('.username').text(profile.getEmail());
}

// Displayed only on /login#admin page
// Logout button action
function google_signout(googleUser) {
    let auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {
	$('button.sign_out').removeClass('btn-primary').addClass('disabled btn-outline-primary');
	$('.avatar, .username').addClass('d-none');
	$('.username').text('');
      console.log('User signed out.');
    });
}

// This gets resolved with the google user, if there is one.
const GOOGLE_PROFILE = $.Deferred();

// This is called on every page ('admin login' callback in _includes/head.html)
function on_load_google_api(){
    console.log('google 1');
    gapi.load('auth2', function(){
	// Retrieve the singleton for the GoogleAuth library and set up the client.
	console.log('google 2');
	auth2 = gapi.auth2.init({
            client_id: login_client_id,
            cookiepolicy: 'single_host_origin'
	}).then((auth)=>{
	    console.log('google 3');
	    if (auth.isSignedIn.get()){
		let profile = auth.currentUser.get().getBasicProfile();
		GOOGLE_PROFILE.resolve(profile);
	    }
	});
    });
}

function print_google_login(profile){
    console.log('Admin logged in as', profile.getName(), '<'+profile.getEmail()+'>');
}

// Print info in the console.
GOOGLE_PROFILE.then(print_google_login);

console.log('loaded login.js')
