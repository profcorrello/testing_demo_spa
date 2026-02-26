// DOM elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const convertBtn = document.getElementById('convert-btn');
const downloadLink = document.getElementById('download-link');
const messageEl = document.getElementById('message');
const themeToggle = document.getElementById('theme-toggle');

let selectedFile = null;

// if loaded directly from the filesystem we can't contact the API
const runningOverFile = window.location.protocol === 'file:';
if (runningOverFile) {
    // show a message and disable interactions
    messageEl.textContent = '⚠️ This page must be served by the backend (see README).';
    document.body.classList.add('file-error');
}

function updateUI() {
    convertBtn.disabled = runningOverFile || !selectedFile;
    if (selectedFile) {
        messageEl.textContent = `Selected: ${selectedFile.name}`;
    } else if (!runningOverFile) {
        messageEl.textContent = '';
        downloadLink.style.display = 'none';
    }
}

function setTheme(isDark) {
    document.body.classList.toggle('dark', isDark);
    themeToggle.textContent = isDark ? '☀️' : '🌙';
    localStorage.setItem('darkTheme', isDark);
}

themeToggle.addEventListener('click', () => {
    setTheme(!document.body.classList.contains('dark'));
});

// initialize theme
setTheme(localStorage.getItem('darkTheme') === 'true');

// drag & drop
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt => {
    dropZone.addEventListener(evt, (e) => {
        e.preventDefault();
        e.stopPropagation();
    });
});

dropZone.addEventListener('dragover', () => {
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    dropZone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length) {
        handleFile(files[0]);
    }
});

dropZone.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', () => {
    if (fileInput.files.length) {
        handleFile(fileInput.files[0]);
    }
});

function handleFile(file) {
    if (file.name.toLowerCase().endsWith('.docx')) {
        selectedFile = file;
    } else {
        alert('Please select a .docx file');
        selectedFile = null;
    }
    updateUI();
}

convertBtn.addEventListener('click', async () => {
    if (runningOverFile) {
        messageEl.textContent = 'Cannot convert without a server. Start the API and open the page over HTTP.';
        return;
    }
    if (!selectedFile) return;
    convertBtn.disabled = true;
    messageEl.textContent = 'Converting...';

    const form = new FormData();
    form.append('file', selectedFile);
    try {
        const res = await fetch('/convert', { method: 'POST', body: form });
        if (!res.ok) {
            const err = await res.text();
            messageEl.textContent = `Error: ${err}`;
            convertBtn.disabled = false;
            return;
        }
        const htmlText = await res.text();
        const blob = new Blob([htmlText], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        downloadLink.href = url;
        downloadLink.download = selectedFile.name.replace(/\.docx$/i, '.html');
        downloadLink.style.display = 'inline-block';
        messageEl.textContent = 'Conversion complete!';
    } catch (e) {
        messageEl.textContent = `Request failed: ${e}`;
    } finally {
        convertBtn.disabled = false;
    }
});
