$(document).ready(function(){

    const canvas1 = document.getElementById('Graph1');
    const canvas2 = document.getElementById('Graph2');
    const canvas3 = document.getElementById('Graph3');
    
    let options = []
    voting.postproc.forEach(element => options.push(element.option));
    let votes = []
    voting.postproc.forEach(element => votes.push(element.votes));
    
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

    new Chart(canvas3, {
        type: 'line',
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
});