import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix token_required to use request.current_user instead of passing argument
content = content.replace(
    'return f(current_user, *args, **kwargs)',
    'request.current_user = current_user\n        return f(*args, **kwargs)'
)

# Find all protected routes and add @token_required
protected_routes = [
    '/api/credits', '/api/chat', '/api/chat/stream', '/api/history/save',
    '/api/history/load', '/api/history/delete', '/api/history/clear',
    '/api/agent/run', '/api/task/plan', '/api/resume/build',
    '/api/memory/delete', '/api/preferences/save', '/api/preferences/load',
    '/api/agent/tasks'
]

for route in protected_routes:
    pattern = rf"(@app\.(post|get)\('{route}'\)\n)def "
    replacement = rf"\1@token_required\ndef "
    content = re.sub(pattern, replacement, content)

# Remove subprocess fallback
# Already done!

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Applied @token_required to protected routes.")
