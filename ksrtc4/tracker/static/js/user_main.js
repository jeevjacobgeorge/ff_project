document.getElementById('searchBtn').addEventListener('click', fetchApi);

async function fetchApi() {
  const from = document.getElementById('fromInput').value;
  const to = document.getElementById('toInput').value;
  const currentDate = new Date();
  const year = currentDate.getFullYear();
  const month = String(currentDate.getMonth() + 1).padStart(2, '0');
  const day = String(currentDate.getDate()).padStart(2, '0');
  const date = `${year}-${month}-${day}`;
  const url = `https://onlineksrtcswift.com/api/resource/searchRoutesV4?fromCityName=${from.toLowerCase()}&toCityName=${to.toLowerCase()}&journeyDate=${date}&mode=oneway`;

  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    if (!Array.isArray(data) || data.length === 0) {
      displayNoResultsMessage();
    } else {
      displayBusResults(data);
    }
  } catch (err) {
    console.error('Error fetching data:', err);
  }
}

function displayNoResultsMessage() {
  const busResults = document.getElementById('busResults');
  busResults.innerHTML = '<p>No bus results found.</p>';
}

function displayBusResults(data) {
  const busResults = document.getElementById('busResults');
  busResults.innerHTML = '';

  const table = document.createElement('table');
  table.classList.add('bus-table');

  // Create table header
  const headers = ['Service Type', 'Departure Time', 'Arrival Time', 'Available Seats'];
  const headerRow = document.createElement('div');
  headerRow.classList.add('bus-header');
  headers.forEach(headerText => {
    const th = document.createElement('div');
    th.textContent = headerText;
    headerRow.appendChild(th);
  });
  table.appendChild(headerRow);

  // Populate table with data
  data.forEach(bus => {
    const row = document.createElement('div');
    row.classList.add('bus-row');
    const serviceTypeCell = document.createElement('div');
    serviceTypeCell.classList.add('bus-service-type');
    serviceTypeCell.textContent = bus.ServiceType;
    row.appendChild(serviceTypeCell);

    const departureTimeCell = document.createElement('div');
    departureTimeCell.classList.add('dept-time-type');
    departureTimeCell.textContent = bus.DepartureTime;
    row.appendChild(departureTimeCell);

    const arrivalTimeCell = document.createElement('div');
    arrivalTimeCell.classList.add('arr-time-type');
    arrivalTimeCell.textContent = bus.ArrivalTime;
    row.appendChild(arrivalTimeCell);

    const availableSeatsCell = document.createElement('div');
    availableSeatsCell.classList.add('avail-seat-type');
    availableSeatsCell.textContent = bus.AvailableSeats;
    row.appendChild(availableSeatsCell);

    // Add event listener to each row
    row.addEventListener('click', function() {
      // Store routescheduleid in localStorage
      localStorage.setItem('routescheduleid', bus.RouteScheduleId);
      // Redirect to another file
      window.location.href = '/tracker/user_map/';
    });

    table.appendChild(row);
  });

  busResults.appendChild(table);
}

function updateClock() {
  var currentTime = new Date();
  var hours = currentTime.getHours();
  var minutes = currentTime.getMinutes();
  var seconds = currentTime.getSeconds();

  // Add leading zeros if necessary
  hours = (hours < 10 ? "0" : "") + hours;
  minutes = (minutes < 10 ? "0" : "") + minutes;
  seconds = (seconds < 10 ? "0" : "") + seconds;

  var timeString = hours + ":" + minutes + ":" + seconds;
  document.getElementById("clock").innerHTML = timeString;
}

setInterval(updateClock, 1000);