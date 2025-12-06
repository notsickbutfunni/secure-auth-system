const API_BASE = 'http://localhost:8000';

let accessToken = null;
let refreshToken = null;

const tabs = document.querySelectorAll('.tab');
const forms = document.querySelectorAll('form[data-tab]');

const registerForm = document.getElementById('register-form');
const loginForm = document.getElementById('login-form');
const registerLog = document.getElementById('register-log');
const loginLog = document.getElementById('login-log');

function setTab(name) {
  tabs.forEach(t => t.classList.toggle('active', t.dataset.tab === name));
  forms.forEach(f => { f.style.display = f.dataset.tab === name ? 'grid' : 'none'; });
}

tabs.forEach(tab => {
  tab.addEventListener('click', () => setTab(tab.dataset.tab));
});

function log(el, message, type = 'info') {
  el.textContent = message;
  el.classList.remove('error', 'success');
  if (type === 'error') el.classList.add('error');
  if (type === 'success') el.classList.add('success');
}

async function api(path, options = {}) {
  const headers = options.headers || {};
  if (accessToken) headers['Authorization'] = `Bearer ${accessToken}`;
  if (options.json) {
    headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.json);
  }
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const text = await res.text();
  let data;
  try { data = text ? JSON.parse(text) : {}; } catch (e) { data = { detail: text }; }
  if (!res.ok) throw { status: res.status, data };
  return data;
}

registerForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  log(registerLog, 'Registering...');
  const form = new FormData(registerForm);
  try {
    const data = await api('/register', {
      method: 'POST',
      json: {
        username: form.get('username'),
        email: form.get('email'),
        password: form.get('password'),
      }
    });
    log(registerLog, `Registered ✓\nUsername: ${data.username}\nEmail: ${data.email}\nTOTP Secret: ${data.totp_secret}`, 'success');
    setTimeout(() => setTab('login'), 1500);
  } catch (err) {
    log(registerLog, `Registration failed (${err.status || ''}): ${err.data?.detail || err}`, 'error');
  }
});

loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  log(loginLog, 'Logging in...');
  const form = new FormData(loginForm);
  try {
    const data = await api('/login', {
      method: 'POST',
      json: {
        username: form.get('username'),
        password: form.get('password')
      }
    });
    accessToken = data.access_token;
    refreshToken = data.refresh_token;
    
    // Store tokens in localStorage
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
    
    log(loginLog, 'Login successful ✓ Redirecting...', 'success');
    
    // Redirect to dashboard
    setTimeout(() => {
      window.location.href = 'dashboard.html';
    }, 1000);
  } catch (err) {
    log(loginLog, `Login failed (${err.status || ''}): ${err.data?.detail || err}`, 'error');
  }
});

