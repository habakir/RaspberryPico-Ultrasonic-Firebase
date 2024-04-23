var firebaseConfig = {
    authDomain: "temperature-and-distance-db.firebaseapp.com",
    databaseURL: "https://temperature-and-distance-db-default-rtdb.europe-west1.firebasedatabase.app/",
    projectId: "temperature-and-distance-db",
    storageBucket: "temperature-and-distance-db.appspot.com",
    messagingSenderId: "1025159877922",
    appId: "1:1025159877922:web:3527a0b156bdd0f43b817b"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const database = firebase.database();

google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);

function drawChart() {
    var data = new google.visualization.DataTable();
    data.addColumn('number', 'Index');  // Using an index number for the X-axis
    data.addColumn('number', 'Temperature');
    data.addColumn('number', 'Distance');

    var options = {
        title: 'Temperature and Distance Monitoring',
        hAxis: { title: 'Measurement Index' },
        vAxis: { title: 'Value' },
        curveType: 'function',
        legend: { position: 'bottom' }
    };

    var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
    var index = 0;  // Initialize index for X-axis

    fetchData(chart, data, options, index);
}

function fetchData(chart, data, options, index) {
    const ref = database.ref();
    ref.limitToLast(1).on('value', function(snapshot) {
        snapshot.forEach(function(childSnapshot) {
            const val = childSnapshot.val();
            data.addRow([index++, val.temperature, val.distance]);  // Increment index with each new data entry
        });
        chart.draw(data, options);
    }, function(error) {
        console.error("Error fetching data", error);
    });
}
