# Introduction

For the final project of the course Introduction to Cyber Security, a demo Django web application was made to demonstrate and solve 5 common vulnerabilities from the OWASP Top 10 (2021) list. The OWASP Top 10 outlines the 10 most critical security risks to web applications and serves as a guide for developers and web application security to identify and mitigate against vulnerabilities. This report will include the set-up instructions for the vulnerable application, explain how users can interact with the app and finally will include a detailed report on each vulnerability and its mitigation. All fixes are commented out in the code. 

## Vulnerabilities: 

### FLAW 1: A02: Cryptographic Failures 
Exact source link: https://github.com/rawatjiya/cybersecurity-project-1/blob/main/core/views.py#L22

Description of flaw 1: 
The application improperly handles user passwords during registration. Instead of using secure hashing mechanism, the passwords are stored directly in plaintext in the database due to the vulnerable code using User.objects.create(). An attacker with access to the database can then read all user passwords, for example through the application terminal: 

from django.contrib.auth.models import User
User.objects.filter(username="testuserbefore").values()

This will expose all the values of the filtered user stored in the database. 

How to fix it: 
To fix this issue, the passwords must be stored using a secure hashing function, such as Djangos built-in functionality. This can be done by using User.objects.create_user(), which hashes the password argument before storing. Any new user registered after the fix will have a hashed password. 

### FLAW 2: A07: Identification and Authentication Failures

Exact source link: https://github.com/rawatjiya/cybersecurity-project-1/blob/main/core/views.py#L43

Description of Flaw 2: 
The applications login mechanism does not properly protect against brute-force attacks, as it permits unlimited login attempts. A session-based counter tracks login attempts for demonstration. Brute force attacks risk access to unauthorized accounts and their user data. 

How to fix it: 
To prevent brute force attacks, where an attacker can repeatedly try different password combinations, we can limit login attempts and temporarily lock accounts after repeated failures. In this fix we apply a limit of MAX_ATTEMPTS = 5 and LOCKOUT_TIME = 300. 

### FLAW 3: A01: Broken Access Control 

Exact source link: https://github.com/rawatjiya/cybersecurity-project-1/blob/main/core/views.py#L134

Description of flaw 3: 
In this flaw, the application fails to enforce control checks to prevent users to act outside of their intended permissions. The application does not verify whether the requested note belongs to the currently authenticated user. As a result, an authenticated user can access notes belonging to other users by modifying the note ID in the URL.  The impact includes unauthorized access to user data and violation of privacy. 

How to fix it: 
To implement proper access control, the application must verify that the requested note belongs to the currently authenticated user, if not the access should be denied: 

if note.owner != request.user:
        return HttpResponse("Unauthorized", status=403)

### FLAW 4: A03: SQL Injection Vulnerability 

Exact source link: https://github.com/rawatjiya/cybersecurity-project-1/blob/main/core/views.py#L152

Description of flaw 4: 
The application includes a search function, which allows users to search for notes in the database. In this flaw, the application constructs SQL queries by embedding them into user inputs, which allows attackers to manipulate the structure and access the database. For example, the input ‘ OR 1=1 --, is embedded directly into the query SELECT * FROM core_note WHERE title LIKE  ‘%’ OR 1=1 -- %’ AND owner_id = 1 which returns all notes in the database. This allows for unintended access to notes that do not belong to the currently authorized user. 

How to fix it:
To fix the vulnerability, the fixed code ensures that the user input is not directly included into the SQL query and is treated strictly as data as is separate to the SQL logic. After implementing the fix, the input ‘OR 1=1 – should not alter the query logic. 

The fixed code looks like the following: 

cursor.execute("SELECT * FROM core_note WHERE title LIKE %s AND owner_id = %s", [f"%{query}%", request.user.id])
        

### FLAW 5: A05: Security Misconfiguration Vulnerability 
Exact source link: https://github.com/rawatjiya/cybersecurity-project-1/blob/main/mysite/settings.py#L28

Description of flaw 5: 
The application is configured with default settings DEBUG = True and ALLOWED_HOSTS = [], which exposes sensitive information when Django displays error pages, for example when trying to navigate to a note that does not exist by changing the URL. The error page will include stack traces, configuration details and can potentially include sensitive data. 

How to fix it: 
To fix the flaw, we can set the mode DEBUG=False and replace the empty list in ALLOWED_HOSTS to the correct domain. This will display an error page without leaking information of the applications internal system and restricts which hosts can interact with the application. 

## Summary

This project demonstrates common OWASP Top 10 (2021) vulnerabilities and their mitigations in a demo Django application. The repository includes screenshots of the flaw before and after the fixes are implemented. In a real-world system, these vulnerabilities would have severe impacts. The impact of the flaws includes unauthorized access to user accounts and sensitive data, database compromise and leakage of internal system information. These risks highlight how improper implementation can directly affect the integrity of a web application. 
