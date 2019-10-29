---
---
$(document).ready(init_page);

// This is how jQuery calls a function to initialize the page.
// It will be executed after all the html, css, and js for the page have been loaded.
function init_page() {
  let url = API_BASE_URL + '/user';
  // get a list of all users from the back end
  $.getJSON(url, null, on_load_users);
  // adds the ‘load_user’ callback to the names menu (<SELECT/>)
  $('#names').change(load_user);
  $('#first_name').focus();
  $('#create_user').on('submit', function(e) {
    submit_data();
    e.preventDefault(); //prevent form from submitting
  });
  populate_services_dropdown();
}

// This is called when the list of all users arrives from the back end.
// It adds all the OPTION menu items to the names menu.
function on_load_users(data) {
  for (var i in data.result) {
    let user = data.result[i];
    let name = user.first_name + ' ' + user.last_name;
    let option = $('<option/>')
      .attr('value', user.user_id)
      .text(name);
    $('#names').append(option);
  }
}

// This is called when the names menu changes (see init_page)
function load_user() {
  let user_id = $(this).val();
  if (typeof user_id != 'undefined') {
    let url = API_BASE_URL + '/user/' + user_id;
    $.getJSON(url, null, on_load_user);
  }
}

// This is called when the data for one user arrives from the back end.
function on_load_user(data) {
  console.log('loaded', data);
  // By default, this table is invisible. Remove the d-none class to make it appear
  $('.show_user').removeClass('d-none');
  // Put data into the table
  $('.show_user .first').text(data.first_name);
  $('.show_user .last').text(data.last_name);
  $('.show_user .color').text(data.color);
  $('#delete_user').on('submit', function(e) {
    delete_user(data);
    e.preventDefault();
  });
}

function get_data() {
  let first_name = $('input#first_name').val();
  let last_name = $('input#last_name').val();
  return { first_name: first_name, last_name: last_name };
}

function submit_data() {
  url = API_BASE_URL + '/user';
  data = get_data();
  console.log('url', url);
  $.post(url, JSON.stringify(data))
    .done(function(msg) {
      success_msg = 'Kid added with user id ' + msg.user_id;
      console.log(success_msg);
      show_alert({ result: 'success' });
    })
    .fail(function(xhr, textStatus, errorThrown) {
      error_msg = 'Unable to add student.';
      console.log(error_msg);
      show_alert({ result: error_msg });
    });
}

function delete_user(data) {
  console.log('delete... ', data);
  //user_id = 'myuserid';
  user_id = data.user_id;
  url = API_BASE_URL + '/user/' + user_id;
  console.log('url', url);
  $.ajax({
    url: url,
    type: 'DELETE',
    success: function(result) {
      success_msg = 'Kid deleted.';
      console.log(success_msg);
      show_alert({ result: 'success' });
    },
  });
}

function populate_services_dropdown() {
    let dropdown = document.getElementById('services-dropdown');
    dropdown.length = 0;

    //let defaultOption = document.createElement('option');
    //defaultOption.text = 'Choose';
    //dropdown.add(defaultOption);

    dropdown.selectedIndex = 0;

    const url = "{{ site.service_types_url }}";

    const request = new XMLHttpRequest();
    request.open('GET', url, true);

    request.onload = function() {
	if (request.status === 200) {
	    //const data = JSON.parse(request.responseText);
	    const data = request.responseText;
	    console.log(data);
	    var x = data.split('\n');
	    let option;
	    for (var i = 1; i < x.length; i++) {
		y = x[i].split('\t');
		x[i] = y;
		console.log(x[i]);
		console.log(x[1]);
		option = document.createElement('option');
		option.text = y[0];
		option.value = y[0];
		dropdown.add(option);
	    }
	} else {
	    // Reached the server, but it returned an error
	}
    };

    request.onerror = function() {
	console.error('An error occurred fetching the JSON from ' + url);
    };
    
    request.send();
}

function show_alert(result_struct) {
  $('.spinner').hide();
  $('.alert-box').show();
  var result = result_struct.result;
  if (result == 'success') {
    $('.alert-box .fail').hide();
    $('.alert-box .success').show();
  } else {
    $('.alert-box .success').hide();
    $('.alert-box .fail').show();
    $('.alert-box .fail .reason').html(result);
  }
  return false;
}
