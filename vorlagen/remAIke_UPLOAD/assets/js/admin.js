// Admin Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    loadJobs();
    setupUploadForm();
});

function loadStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-videos').textContent = data.totalVideos;
            document.getElementById('active-jobs').textContent = data.activeJobs;
            document.getElementById('comparisons').textContent = data.comparisons;
            document.getElementById('storage').textContent = data.storage;
        })
        .catch(error => console.error('Error loading stats:', error));
}

function loadJobs() {
    fetch('/api/jobs')
        .then(response => response.json())
        .then(jobs => {
            const tbody = document.getElementById('jobs-tbody');
            tbody.innerHTML = '';

            jobs.forEach(job => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${job.id.substring(0, 8)}</td>
                    <td>${job.name}</td>
                    <td><span class="badge bg-${getStatusColor(job.status)}">${job.status}</span></td>
                    <td>
                        <div class="progress" style="width: 100px;">
                            <div class="progress-bar" style="width: ${job.progress}%"></div>
                        </div>
                        ${job.progress}%
                    </td>
                    <td>${new Date(job.created_at).toLocaleDateString()}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" onclick="viewJob('${job.id}')">View</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(error => console.error('Error loading jobs:', error));
}

function getStatusColor(status) {
    switch(status) {
        case 'completed': return 'success';
        case 'processing': return 'warning';
        case 'failed': return 'danger';
        default: return 'secondary';
    }
}

function setupUploadForm() {
    const form = document.getElementById('upload-form');
    const progressDiv = document.getElementById('upload-progress');
    const progressBar = progressDiv.querySelector('.progress-bar');

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(form);
        progressDiv.style.display = 'block';
        progressBar.style.width = '0%';

        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            progressBar.style.width = '100%';
            alert('Upload erfolgreich! Job ID: ' + data.jobId);
            form.reset();
            loadStats();
            loadJobs();
        })
        .catch(error => {
            console.error('Upload error:', error);
            alert('Upload fehlgeschlagen');
        });
    });
}

function viewJob(jobId) {
    // Placeholder for job details view
    alert('Job Details für: ' + jobId);
}

// Auto refresh every 30 seconds
setInterval(() => {
    loadStats();
    loadJobs();
}, 30000);
