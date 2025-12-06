const API_BASE = 'http://localhost:8000';

let accessToken = localStorage.getItem('accessToken');
let refreshToken = localStorage.getItem('refreshToken');

const sessionState = document.getElementById('session-state');
const profileBox = document.getElementById('profile');
const sessionLog = document.getElementById('session-log');
const btnProfile = document.getElementById('btn-profile');
const btnLogout = document.getElementById('btn-logout');
const btnSecret = document.getElementById('btn-secret');
const secretMessage = document.getElementById('secret-message');

// Tabs and sections
const tabs = document.querySelectorAll('.tab[data-section]');
const sections = document.querySelectorAll('.section');
const docButtons = document.querySelectorAll('.doc-btn');
const docContent = document.getElementById('doc-content');

// Redirect to login if not authenticated
if (!accessToken) {
  window.location.href = 'index.html';
}

// Tab switching
tabs.forEach(tab => {
  tab.addEventListener('click', () => {
    const sectionName = tab.dataset.section;
    tabs.forEach(t => t.classList.toggle('active', t === tab));
    sections.forEach(s => {
      s.style.display = s.id === `${sectionName}-section` ? 'block' : 'none';
    });
  });
});

// Documentation loading
const docs = {
  api: `# API Reference

## Authentication Endpoints

### POST /register
Register a new user account with TOTP 2FA setup.

**Request Body:**
\`\`\`json
{
  "username": "myuser",
  "email": "user@example.com",
  "password": "SecureP@ss123!"
}
\`\`\`

**Response (200):**
\`\`\`json
{
  "msg": "User registered successfully",
  "username": "myuser",
  "email": "user@example.com",
  "totp_secret": "BASE32SECRETHERE"
}
\`\`\`

---

### POST /login
Authenticate user and receive JWT access & refresh tokens.

**Request Body:**
\`\`\`json
{
  "username": "myuser",
  "password": "SecureP@ss123!",
  "totp": "123456"
}
\`\`\`

**Response (200):**
\`\`\`json
{
  "msg": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
\`\`\`

---

### POST /token/refresh
Refresh an expired access token using a valid refresh token.

**Request Body:**
\`\`\`json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
\`\`\`

**Response (200):**
\`\`\`json
{
  "msg": "Token refreshed successfully",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
\`\`\`

---

### POST /logout
Invalidate all refresh tokens for the user.

**Request Body:**
\`\`\`json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
\`\`\`

**Response (200):**
\`\`\`json
{
  "msg": "Logged out successfully"
}
\`\`\`

---

### GET /users/me
Get current user profile (requires valid access token).

**Headers:**
\`\`\`
Authorization: Bearer <access_token>
\`\`\`

**Response (200):**
\`\`\`json
{
  "id": 1,
  "username": "myuser",
  "email": "user@example.com",
  "totp_enabled": true,
  "created_at": "2025-12-06T10:30:00"
}
\`\`\``,

  architecture: `# Architecture Overview

## System Components

### 1. Backend (FastAPI)
- **Framework**: FastAPI with Uvicorn
- **Database**: SQLite with SQLModel ORM
- **Authentication**: JWT with RS256 asymmetric signing
- **Password Hashing**: Argon2 (memory-hard algorithm)
- **2FA**: TOTP (Time-based One-Time Password)

### 2. Security Features
- **Encryption**: AES-GCM for sensitive data
- **Digital Signatures**: RSA-PSS for message integrity
- **Key Derivation**: HKDF for Diffie-Hellman shared secrets
- **Secure Randomness**: Python secrets module

### 3. Frontend
- **Technology**: Vanilla HTML/CSS/JavaScript
- **Storage**: localStorage for token persistence
- **API Communication**: Fetch API with Bearer tokens
- **Design**: Soft Miku-inspired color palette

## Data Flow

1. **Registration**: User → Hash password → Generate TOTP secret → Store in DB
2. **Login**: User credentials → Verify password → Check TOTP → Issue JWT tokens
3. **Authenticated Requests**: Access token → Verify signature → Check expiry → Allow access
4. **Token Refresh**: Refresh token → Validate → Issue new access token

## Security Layers

- **Transport**: HTTPS recommended for production
- **Storage**: Encrypted refresh tokens in database
- **Validation**: Input sanitization and validation
- **Error Handling**: Generic error messages to prevent information leakage`,

  security: `# Security Analysis

## Implemented Security Features

### 1. Password Security
- **Argon2**: Memory-hard password hashing algorithm
- **Requirements**: Min 8 chars, uppercase, lowercase, digit, special char
- **No Plain Storage**: Passwords never stored in plain text

### 2. Multi-Factor Authentication
- **TOTP**: RFC 6238 compliant time-based codes
- **Secret Generation**: Cryptographically secure random base32
- **Window**: ±30 seconds validity window

### 3. Token Security
- **Algorithm**: RS256 (RSA with SHA-256)
- **Key Size**: 2048-bit RSA keys
- **Expiry**: Access tokens (15 min), Refresh tokens (7 days)
- **Storage**: Refresh tokens encrypted in database

### 4. Encryption
- **AES-GCM**: Authenticated encryption with 256-bit keys
- **Nonce**: 96-bit random nonce per encryption
- **AAD**: Additional Authenticated Data for context binding

### 5. Input Validation
- **Username**: 3-32 alphanumeric chars, underscore, dash
- **Email**: RFC-compliant email format validation
- **Password**: Strength validation with multiple requirements
- **Sanitization**: Dangerous characters stripped

## Threat Mitigation

### ✅ Protected Against
- Brute Force: Strong password requirements + Argon2
- Token Theft: Short-lived access tokens
- Replay Attacks: Nonce in AES-GCM, JWT expiry
- SQL Injection: ORM parameterized queries
- XSS: No inline scripts, sanitized inputs

### ⚠️ Additional Recommendations
- Rate limiting on login attempts
- HTTPS enforcement in production
- CORS restrictions for production domains
- Security headers (HSTS, CSP, X-Frame-Options)
- Regular key rotation
- Audit logging for security events

## Best Practices Applied

1. **Principle of Least Privilege**: Minimal data exposure in tokens
2. **Defense in Depth**: Multiple security layers
3. **Secure Defaults**: Strong algorithms, no weak ciphers
4. **Zero Trust**: Every request validated independently`
};

function renderMarkdown(text) {
  return text
    .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/^\- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n\n/g, '<br><br>');
}

docButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    const docName = btn.dataset.doc;
    docButtons.forEach(b => b.classList.toggle('active', b === btn));
    docContent.innerHTML = renderMarkdown(docs[docName]);
  });
});

// Load first doc by default
docContent.innerHTML = renderMarkdown(docs.api);

function log(el, message, type = 'info') {
  el.textContent = message;
  el.classList.remove('error', 'success');
  if (type === 'error') el.classList.add('error');
  if (type === 'success') el.classList.add('success');
}

function updateSessionState() {
  if (accessToken) {
    sessionState.textContent = 'Authenticated';
    sessionState.style.color = '#39ffb4';
  } else {
    sessionState.textContent = 'Not Authenticated';
    sessionState.style.color = '#ff6b9d';
    profileBox.innerHTML = '';
  }
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

btnProfile.addEventListener('click', async () => {
  if (!accessToken) {
    log(sessionLog, 'Not authenticated. Login first.', 'error');
    window.location.href = 'index.html';
    return;
  }
  log(sessionLog, 'Loading profile...');
  try {
    const data = await api('/users/me');
    profileBox.innerHTML = `
      <div><span>ID</span><div>${data.id}</div></div>
      <div><span>Username</span><div>${data.username}</div></div>
      <div><span>Email</span><div>${data.email}</div></div>
      <div><span>TOTP Enabled</span><div>${data.totp_enabled}</div></div>
      <div><span>Created</span><div>${data.created_at}</div></div>
    `;
    log(sessionLog, 'Profile loaded ✓', 'success');
  } catch (err) {
    if (err.status === 401 && refreshToken) {
      const refreshed = await attemptRefresh();
      if (refreshed) return btnProfile.click();
    }
    log(sessionLog, `Profile failed (${err.status || ''}): ${err.data?.detail || err}`, 'error');
    if (err.status === 401) {
      setTimeout(() => { window.location.href = 'index.html'; }, 2000);
    }
  }
});

btnLogout.addEventListener('click', async () => {
  if (!refreshToken) {
    accessToken = null;
    localStorage.clear();
    updateSessionState();
    log(sessionLog, 'No refresh token; session cleared.', 'success');
    setTimeout(() => { window.location.href = 'index.html'; }, 1000);
    return;
  }
  log(sessionLog, 'Logging out...');
  try {
    await api('/logout', { method: 'POST', json: { refresh_token: refreshToken } });
    accessToken = null;
    refreshToken = null;
    localStorage.clear();
    updateSessionState();
    log(sessionLog, 'Logged out ✓', 'success');
    setTimeout(() => { window.location.href = 'index.html'; }, 1000);
  } catch (err) {
    log(sessionLog, `Logout failed (${err.status || ''}): ${err.data?.detail || err}`, 'error');
  }
});

btnSecret.addEventListener('click', () => {
  const name = prompt('What is your name? 🎤');
  
  if (!name) {
    secretMessage.style.display = 'none';
    return;
  }
  
  secretMessage.style.display = 'block';
  
  if (name.toLowerCase() === 'adil') {
    secretMessage.innerHTML = "Hello teacher, как вы? Я хотела сказать, что весь семестр вы на самом деле мотивировали меня, благодаря вашему трудолюбию и вашим навыкам обучать, мне очень захотелось стать как вы, и в самом деле моя продуктивность очень сильно взросла, и все это ваша заслуга. Я наконец получаю 100% удовольствия от всего чем занимаюсь, это невероятно. Когда вы написали I don't work with sdu anymore мне стало очень грустно, вы такого не заслужили и всегда будете самым лучшим тичерем в памяти многих студентов! Желаю вам успехов и счастья, вы мой кумир!";
  } else {
    secretMessage.innerHTML = `Hi ${name}! That's not for you, sorry`;
  }
});

async function attemptRefresh() {
  if (!refreshToken) return false;
  log(sessionLog, 'Refreshing access token...');
  try {
    const data = await api('/token/refresh', { method: 'POST', json: { refresh_token: refreshToken } });
    accessToken = data.access_token;
    localStorage.setItem('accessToken', accessToken);
    updateSessionState();
    log(sessionLog, 'Token refreshed ✓', 'success');
    return true;
  } catch (err) {
    log(sessionLog, `Refresh failed (${err.status || ''}): ${err.data?.detail || err}`, 'error');
    localStorage.clear();
    return false;
  }
}

updateSessionState();
