/**
 * Kinesis AI — Dashboard Analytics & Chart.js Visualizations
 * SIH 2026 Edition
 */

document.addEventListener('DOMContentLoaded', () => {
    initFitnessProgressChart();
    initSportsRadarChart();
});

function initFitnessProgressChart() {
    const ctx = document.getElementById('fitnessProgressChart');
    if (!ctx) return;

    // Use embedded JSON dataset or fallback sample
    const rawData = window.kinesisFitnessHistory || [
        { date: 'Mon', score: 78 },
        { date: 'Tue', score: 82 },
        { date: 'Wed', score: 85 },
        { date: 'Thu', score: 80 },
        { date: 'Fri', score: 88 },
        { date: 'Sat', score: 92 },
        { date: 'Sun', score: 90 }
    ];

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: rawData.map(d => d.date),
            datasets: [{
                label: 'Form Quality Score',
                data: rawData.map(d => d.score),
                borderColor: '#00f2fe',
                backgroundColor: 'rgba(0, 242, 254, 0.12)',
                borderWidth: 3,
                fill: true,
                tension: 0.35,
                pointBackgroundColor: '#00ff87',
                pointBorderColor: '#fff',
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    min: 40,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.06)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8' }
                }
            }
        }
    });
}

function initSportsRadarChart() {
    const ctx = document.getElementById('sportsSkillRadarChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Shooting', 'Dribbling', 'Agility', 'Pull Shot', 'Cover Drive', 'Bowling'],
            datasets: [{
                label: 'Your Current Biomechanics Score',
                data: window.kinesisSportsSkillData || [82, 75, 88, 80, 85, 70],
                backgroundColor: 'rgba(0, 255, 135, 0.2)',
                borderColor: '#00ff87',
                borderWidth: 2,
                pointBackgroundColor: '#00f2fe',
                pointBorderColor: '#fff',
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                r: {
                    min: 0,
                    max: 100,
                    ticks: { display: false, stepSize: 20 },
                    grid: { color: 'rgba(255, 255, 255, 0.08)' },
                    angleLines: { color: 'rgba(255, 255, 255, 0.12)' },
                    pointLabels: {
                        color: '#cbd5e1',
                        font: { size: 12, weight: '600' }
                    }
                }
            }
        }
    });
}
