let dropdown = document.getElementById('services-dropdown');
dropdown.length = 0;

//let defaultOption = document.createElement('option');
//defaultOption.text = 'Choose';
//dropdown.add(defaultOption);

dropdown.selectedIndex = 0;

const url =
  'https://docs.google.com/spreadsheets/d/1kNrnfhhqY0vPJ4yB61eWEeyBtcqn-vCUHffBN2aOBUI/export?gid=0&format=tsv';

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
