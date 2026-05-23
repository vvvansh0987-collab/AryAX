import re

with open('public/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Add fetch interceptor at the top
interceptor = """
// ── JWT AUTH INTERCEPTOR ──────────────────────────────
const originalFetch = window.fetch;
window.fetch = async function() {
    let [resource, config] = arguments;
    if (typeof resource === 'string' && resource.startsWith('/api/') && !resource.includes('/api/login') && !resource.includes('/api/signup')) {
        const token = localStorage.getItem('aryax-token');
        if (token) {
            config = config || {};
            config.headers = config.headers || {};
            config.headers['Authorization'] = `Bearer ${token}`;
            arguments[1] = config;
        }
    }
    return originalFetch.apply(this, arguments);
};
"""
if "JWT AUTH INTERCEPTOR" not in js:
    js = interceptor + "\n" + js

# 2. Update loginSuccess signature
js = js.replace('async function loginSuccess(username, credits) {', 'async function loginSuccess(username, credits, token) {\n    if (token) localStorage.setItem("aryax-token", token);')

# 3. Update authForm.onsubmit
js = js.replace('if (r.ok) loginSuccess(d.username || u, d.credits);', 'if (r.ok) loginSuccess(d.username || u, d.credits, d.token);')

# 4. Update auto-login
js = js.replace('loginSuccess(saved, d.credits);', 'loginSuccess(saved, d.credits, localStorage.getItem("aryax-token"));')

# 5. Logout logic to clear token
js = js.replace("localStorage.removeItem('aryax-user');", "localStorage.removeItem('aryax-user');\n    localStorage.removeItem('aryax-token');")

with open('public/script.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("Frontend JWT patched successfully.")
