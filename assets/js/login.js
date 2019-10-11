$(document).ready(load_admins);

/*
This file enables the "admin" navbar button for admins.

It assumes you have a google-based email (either gmail or GSuite).
The process is described here:
   https://developers.google.com/identity/sign-in/web/sign-in

To be an admin, add your google-based email to the Google Sheets below (admins_url).
This sheet is publicly readable, but can only be edited by a Helperbees admin.
If you're working on a copy of this repo, replace this url with your own,
and configure your own credentials at the Google developers site (see above).

How this code works:

This code is loaded in default.html and triggered by an invisible DIV's data-onsuccess attribute.
The 'd-none' class makes this button invisible:
    <!-- hidden button, used for admin login -->
    <script src="assets/js/login.js"></script>
    <div class="g-signin2 d-none" data-onsuccess="onSignIn"></div>

head.html adds a meta tag and loads the Google web APIs

If you're logged in as a Google user, and the user's email is found in the admins_url,
then you're an admin and we make the Admin navbar tab visible.
*/

// replace this url with your own, and put your own admins into it.
admins_url = 'https://docs.google.com/spreadsheets/d/1ybEhA4NazoiHf5khx7khDHnlLmpx7OExWxoLO32Rpbc/export?gid=0&format=tsv';

// When loaded, admins contains an array of legit admin emails
var admins = null;


/* Send this token to the back end.
   This is a JWT token - it's digitally signed to prove the user's identity.
   Visit jwt.io to decode it. */
var id_token = null; 

function load_admins(){
    $.get(admins_url).done(on_load_admins);
}

function on_load_admins(data){
    admins = data.split('\r\n').slice(1);
}

function onSignIn(googleUser){
    let profile = googleUser.getBasicProfile();
    id_token = googleUser.getAuthResponse().id_token;
    let email = profile.getEmail();
    if (admins.includes(email)){
	console.log("Logged in as admin:", email);
	console.log('with id_token = "'+id_token.substr(0,10)+'..."');
	$('.tab-admin').removeClass('d-none');
    } else {
	console.log('Not an admin');
    }
}
