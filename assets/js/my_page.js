---
---
$(document).ready(()=> {
    USER_INFO.then(init_about_me);
    $('button.logout').click(logout);
});


// If we're logged in, this will wait for USER_INFO to fetch the user's info.
// Then use it to fill in the form.
function init_about_me(user_info){
    for (var field in user_info){
	let value = user_info[field];
	$('form#about_me #'+field).val(value);
    }
    let site_url = "{{ site.url }}";
    let link_url = site_url + '/login#' + user_info.login_code;
    let link = $('<a/>').attr('href', link_url).text(link_url);
    $('div#login_link').append(link);
    $('.logging-in').addClass('d-none');
    $('form#about_me').removeClass('d-none');
}

function logout(){
    delete_cookie(LOGIN_COOKIE);
    window.location.pathname = '/';
    return false;
}
