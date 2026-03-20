const API = 'http://127.0.0.1:8000';

function getCsrf() {
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? m[1] : '';
}

async function apiFetch(url, opts = {}) {
    return fetch(API + url, {
        credentials: 'include',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf(), ...(opts.headers || {}) },
        ...opts
    });
}

function toast(msg, type = 'success') {
    const wrap = document.getElementById('toastWrap');
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}" style="color:${type === 'success' ? '#28a745' : '#dc3545'}"></i><span>${msg}</span>`;
    wrap.appendChild(el);
    setTimeout(() => el.remove(), 3500);
}

async function logout() {
    try { await apiFetch('/api/logout/', { method: 'POST' }); } catch(e) {}
    window.location.href = 'home.html';
}

async function loadOutpasses() {
    const state = document.getElementById('tableState');
    state.innerHTML = '<div class="spinner-wrap"><div class="spinner"></div><p>Loading...</p></div>';

    try {
        const res = await apiFetch('/api/my-outpasses/');
        if (res.status === 403 || res.redirected) { window.location.href = 'home.html'; return; }
        const data = await res.json();

        if (!data.success) {
            state.innerHTML = `<div class="empty"><i class="fas fa-exclamation-circle"></i>${data.message}</div>`;
            return;
        }

        if (data.data.length === 0) {
            state.innerHTML = '<div class="empty"><i class="fas fa-file-alt"></i>No outpass requests yet. Create your first one!</div>';
            return;
        }

        state.innerHTML = `
            <table>
                <thead><tr>
                    <th>ID</th><th>Destination</th><th>Departure</th>
                    <th>Return</th><th>Status</th><th>Hostel</th>
                </tr></thead>
                <tbody>${data.data.map(o => `
                    <tr>
                        <td>#${o.id}</td>
                        <td>${o.destination}</td>
                        <td>${o.departure_date}</td>
                        <td>${o.return_date}</td>
                        <td><span class="badge ${o.status}">${o.status}</span></td>
                        <td><span class="badge ${o.hostel_status}">${o.hostel_status}</span></td>
                    </tr>
                `).join('')}</tbody>
            </table>`;
    } catch(e) {
        state.innerHTML = '<div class="empty"><i class="fas fa-wifi"></i>Cannot connect to server.</div>';
    }
}

async function markIn() {
    try {
        const res = await apiFetch('/api/mark-in/', { method: 'POST', body: JSON.stringify({}) });
        const data = await res.json();
        toast(data.message, data.success ? 'success' : 'error');
        if (data.success) loadOutpasses();
    } catch(e) {
        toast('Failed to mark IN', 'error');
    }
}

function openCreateModal() {
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    const min = now.toISOString().slice(0, 16);
    document.getElementById('timeOut').min = min;
    document.getElementById('returnDate').min = min;
    document.getElementById('outpassForm').reset();
    document.getElementById('formMsg').className = 'api-msg';
    document.getElementById('createModal').classList.add('active');
}

function closeModal() {
    document.getElementById('createModal').classList.remove('active');
}

async function submitOutpass() {
    const btn = document.getElementById('submitBtn');
    const msg = document.getElementById('formMsg');
    const purpose = document.getElementById('purpose').value.trim();
    const destination = document.getElementById('destination').value.trim();
    const timeOut = document.getElementById('timeOut').value;
    const returnDate = document.getElementById('returnDate').value;

    msg.className = 'api-msg';
    if (!purpose || !destination || !timeOut || !returnDate) {
        msg.className = 'api-msg error';
        msg.textContent = 'All fields are required.';
        return;
    }

    btn.disabled = true;
    btn.textContent = 'Submitting...';

    try {
        const formData = new FormData();
        formData.append('purpose', purpose);
        formData.append('destination', destination);
        formData.append('time_out', timeOut);
        formData.append('return_date', returnDate);

        const res = await fetch(`${API}/api/create-outpass/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCsrf() },
            credentials: 'include',
            body: formData
        });
        const data = await res.json();

        if (data.success) {
            toast('Outpass request submitted!', 'success');
            closeModal();
            loadOutpasses();
        } else {
            msg.className = 'api-msg error';
            msg.textContent = data.message || 'Submission failed.';
        }
    } catch(e) {
        msg.className = 'api-msg error';
        msg.textContent = 'Cannot connect to server.';
    } finally {
        btn.disabled = false;
        btn.textContent = 'Submit Request';
    }
}

// Init
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('timeOut').addEventListener('change', function() {
        document.getElementById('returnDate').min = this.value;
    });

    document.getElementById('createModal').addEventListener('click', function(e) {
        if (e.target === this) closeModal();
    });

    loadOutpasses();
    setInterval(loadOutpasses, 30000);
});
