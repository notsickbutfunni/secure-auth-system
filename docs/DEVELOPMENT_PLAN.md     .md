## 🗓️ till 15th week Development Plan

### **Day 1 — Project Setup & Planning** (19.11)
- Initialize GitHub repo  
- Add project structure, README, LICENSE  
- Write development plan  
- Define crypto stack
- Add `.gitignore`  
  
**Deliverables:** Repo, skeleton structure, initial README, development plan.

---

### **Day 2 — Environment Setup & Base FastAPI App**  (22.11)
- Install dependencies  
- Create FastAPI structure (`main.py`)  
- Virtual environment setup  

**Deliverables:** Working FastAPI server.

---

### **Day 3 — Database Design & User Model** (04.12)
- Configure DB (SQLite)
- Create User model with `id`, `username`, `email`
- Initialize DB table / storage

**Deliverables:** Database + user table ready.

---

### **Day 4 — Password Hashing (bcrypt) + Input Validation** (22.11 - ???)
- Implement argon hashing & verification  
- Add other crypto tools(will define soon)  
- Prevent weak passwords & malformed inputs  

**Deliverables:** `/register` endpoint, unit test for hashing.

---

### **Day 5 — JWT Authentication (RSA-Signed)** (23.11)
- Generate RSA key pair  
- RS256-signed JWT tokens  
- Access + refresh token logic with expiration & claims

**Deliverables:** `app/secure.py`, `/login` endpoint, key storage in `/keys/`.

---

### **Day 6 — Symmetric Encryption (AES-256-GCM)**
- AES-256-GCM for encrypting refresh tokens, backup codes  
- Handle IV, authentication tag, and key rotation  

**Deliverables:**  with encrypt/decrypt functions and tests.

---

### **Day 7 — Asymmetric Encryption (RSA)**
- RSA encryption for wrapping AES session keys  
- OAEP padding implementation  

**Deliverables:** `app/secure.py` with unit tests.

---

### **Day 8 — Digital Signatures (RSA-PSS)**
- Sign server-issued tokens  
- Verify signatures in middleware  
- Audit logging using signatures  

**Deliverables:** `app/secure.py` and unit tests.

---

### **Day 9 — Diffie-Hellman From Scratch**
- Implement classical DH in Python (`pow()`)  
- Large prime + generator  
- Compute shared secret  
- Derive AES key using HKDF  

**Deliverables:** `app/secure.py` with unit tests and documentation.

---

### **Day 10 — Key Management, Secure Randomness, Error Handling**
- Use `secrets` for random generation  
- Key rotation script  
- Secure key storage policies  
- Full error handling for crypto modules  
- Input sanitization  

**Deliverables:** `/scripts/rotate_keys.py`, `auth/errors.py`.

---

### **Day 11 — Full Documentation + Security Analysis**
- Create:  
  - `ARCHITECTURE.md`  
  - `SECURITY_ANALYSIS.md`  
  - `API_DOCUMENTATION.md`  
  - `USER_MANUAL.md`  
- Add diagrams   

**Deliverables:** Complete `/docs/` folder.

---

### **Day 12 — Presentation & Final Polishing**
- Prepare slides (10–15 min)  
- Live demo scenario  
- Rehearse demo sequence  
- Final GitHub cleanup, license, and re-tests  

**Deliverables:**  
- `presentation/slides.pdf`  
- `presentation/demo_script.md`  
- Final repo ready for submission

---

## 📁 Repository Structure
```
secure-auth-system/
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
├── src/
│ ├── main.py
│ ├── config.py
│ ├── database.py
│ ├── auth/
│ └── users/
├── tests/
├── docs/
│ ├── DEVELOPMENT_PLAN.md
│ ├── ARCHITECTURE.md
│ ├── SECURITY_ANALYSIS.md
│ ├── USER_MANUAL.md
│ └── API_DOCUMENTATION.md
├── presentation/
└── scripts/
```