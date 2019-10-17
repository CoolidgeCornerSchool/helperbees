// see
// https://developers.google.com/identity/sign-in/web/reference

const google_client_id = '958880294296-npvqs3418t62qbcvaqb05qb0briht2oe.apps.googleusercontent.com';

// promise that would be resolved when gapi would be loaded
const gapiPromise = (function(){
    var deferred = $.Deferred();
    zot = deferred;
    window.onLoadCallback = function(){
	console.log('window loaded');
	deferred.resolve(gapi);
    };
    return deferred.promise()
}());

//var authInited = gapiPromise.then(function(){
//    console.log('authInited', "gapi=", gapi);
//    gapi.auth2.init({client_id: google_client_id});
//});

const google_client = {

    auth2: null,  // The Sign-In client object.

    load: function() {
	// Initializes the Sign-In client.
	let self = this;
	console.log('loading gapi', self);
	gapiPromise.then(()=>
			 {
			     console.log('now loading');
			     gapi.load('auth2', self.on_loaded.call(self));
			 });
    },

    on_loaded: function(){
	console.log('is_loaded', this, gapi);
	// Retrieve the singleton for the GoogleAuth library and set up the client.
	this.auth2 = gapi.auth2.init({ client_id: google_client_id });

	// Handle successful sign-ins.
	function onSuccess (user) {
	    console.log('Signed in as ' + user.getBasicProfile().getName());
	};

	// Handle sign-in failures.
	function onFailure (error) {
	    console.log(error);
	};

	// Attach the click handler to the sign-in button
	// https://developers.google.com/identity/sign-in/web/reference#googleauthattachclickhandlercontainer_options_onsuccess_onfailure
	// auth2.attachClickHandler('signin-button', {}, onSuccess, onFailure);
    },

    is_signed_in: function(){
	if (this.auth2 == null){
	    return false;
	}
	return this.auth2.isSignedIn.get();
    },

    user_profile: function(){
	if (this.auth2 == null){
	    return null;
	}
	return auth2.currentUser.get().getBasicProfile();
    },

    get_id_token: function(){
	if (this.auth2 == null){
	    return null;
	}
	return auth2.currentUser.get().getAuthResponse().id_token;
    }
}

$(document).ready(google_client.load.call(google_client));
