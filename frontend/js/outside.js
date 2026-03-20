const video = document.getElementById('video');
const profilePreview = document.getElementById('profilePreview');

profilePreview.addEventListener('click', function() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function(stream) {
            video.style.display = 'block';
            profilePreview.style.display = 'none';
            video.srcObject = stream;

            setTimeout(function() {
                const canvas = document.createElement('canvas');
                canvas.width = 120;
                canvas.height = 120;
                canvas.getContext('2d').drawImage(video, 0, 0, 120, 120);

                profilePreview.src = canvas.toDataURL('image/png');
                profilePreview.style.display = 'block';
                video.style.display = 'none';
                stream.getTracks().forEach(t => t.stop());
            }, 3000);
        })
        .catch(() => alert('Camera permission denied'));
});

// Set current date and time
const today = new Date();
const pad = n => String(n).padStart(2, '0');
document.getElementById('date').value =
    `${pad(today.getDate())}-${pad(today.getMonth() + 1)}-${today.getFullYear()}`;
document.getElementById('time').value =
    `${pad(today.getHours())}:${pad(today.getMinutes())}`;

function validation() {
    const name = document.getElementById('name').value;
    const regno = document.getElementById('regno').value;

    if (!name)   { alert('Enter Name'); return; }
    if (!regno)  { alert('Enter Register Number'); return; }

    alert('Success!');
}
