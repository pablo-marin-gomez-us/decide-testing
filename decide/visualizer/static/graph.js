$(document).ready(function(){

    const canvas1 = document.getElementById('Graph1');
    const canvas2 = document.getElementById('Graph2');
    const canvas3 = document.getElementById('Graph3');

    total_seats = voting.seats

    let options = []
    voting.postproc.forEach(element => options.push(element.option));

    let votes = []
    voting.postproc.forEach(element => votes.push(element.votes));

    let seats = []
    voting.postproc.forEach(element => seats.push(element.seats));

    let seats_percentage = []
    voting.postproc.forEach(element => seats_percentage.push((element.seats/total_seats)*100));

    new Chart(canvas1, {
        type: 'pie',
        data: {
        labels: options,
        datasets: [{
            label: 'Votes',
            data: votes,
            borderWidth: 1
        }]
        },
        options: {
        scales: {
            y: {
            beginAtZero: true
            }
        }
        }
    });

    new Chart(canvas2, {
        type: 'bar',
        data: {
        labels: options,
        datasets: [{
            label: 'Seats',
            data: seats,
            borderWidth: 1
        }]
        },
        options: {
        scales: {
            y: {
            beginAtZero: true
            }
        }
        }
    });

    new Chart(canvas3, {
        type: 'doughnut',
        data: {
        labels: options,
        datasets: [{
            label: '% of representation',
            data: seats_percentage,
            borderWidth: 1
        }]
        },
        options: {
        scales: {
            y: {
            beginAtZero: true
            }
        }
        }
    });
});
