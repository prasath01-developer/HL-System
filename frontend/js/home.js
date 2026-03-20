const API = 'http://127.0.0.1:8000';

async function getCsrf() {
    try {
        await fetch(`${API}/api/csrf-token/`, { credentials: 'include' });
    } catch(e) {}
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
}

document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const btn = document.getElementById('loginBtn');
    const msg = document.getElementById('msg');
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    msg.className = 'msg';
    msg.textContent = '';
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span>Signing in...';

    try {
        const csrf = await getCsrf();
        const res = await fetch(`${API}/api/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
            credentials: 'include',
            body: JSON.stringify({ username, password })
        });
        const data = await res.json();

        if (data.success) {
            msg.className = 'msg success';
            msg.textContent = 'Login successful! Redirecting...';
            setTimeout(() => {
                window.location.href = data.user.is_admin ? 'outside.html' : 'insidelock.html';
            }, 600);
        } else {
            msg.className = 'msg error';
            msg.textContent = data.message || 'Invalid credentials.';
            btn.disabled = false;
            btn.textContent = 'Login';
        }
    } catch(err) {
        msg.className = 'msg error';
        msg.textContent = 'Cannot connect to server. Make sure the backend is running.';
        btn.disabled = false;
        btn.textContent = 'Login';
    }
});
