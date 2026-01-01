# Expanded security examples (SQLi, XSS-like patterns, command injection)

def insecure_sql(user):
    return f"SELECT * FROM users WHERE name = '{user}'"

def secure_sql(user):
    return ("SELECT * FROM users WHERE name = %s", (user,))

def insecure_command(ip):
    import os
    os.system("ping " + ip)

def secure_command(ip):
    import subprocess
    subprocess.run(["ping", ip])
