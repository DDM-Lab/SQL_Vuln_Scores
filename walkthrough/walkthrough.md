# Introduction

The goal of this problem set is to expose participants to [SQL injection vulnerabilities](https://owasp.org/www-community/attacks/SQL_Injection).

SQL injections can occur in online web applications that do not perform sanitization on user inputs. That means, when you create a form in a web application (such as a username and password login), you should be mindful on how the operations you perform with the user's input are used in the rest of your code.

Each challenge below, has a slightly different vulnerability.

*You only need to complete one of the challenges but choose wisely.*


## Challenge 1 (IT Department)

```
' UNION SELECT flag FROM flags --
```

What's happening:

- The `'` closes the current SQL query’s string.
- `UNION SELECT` allows combining the results of two queries.
- `flag FROM flags` is pulling a sensitive piece of data from a flags table.
- `--` comments out the rest of the original SQL query so it doesn’t interfere.

Effect: This tricks the database into returning the flag instead of normal data.

## Challenge 2 (Root Crdentials DB)
```
' UNION SELECT flag, NULL, NULL FROM hidden_flags --
```

What’s happening:

- The table `hidden_flags` likely has 3 columns.
- `SQL UNION` requires the same number of columns as the original query.
- `NULL, NULL` are placeholders to match the expected column count.

Effect: It returns the flag from `hidden_flags`, aligning with the expected column structure.

## Challenge 3 (Logs Endpoint)

```
' UNION SELECT secret_code, NULL FROM library_secrets --
```

What's happening:

- Similar to Challenge 2, but with only 2 columns this time.
- `library_secret`s contains a `secret_code` the attacker wants to extract.
- The second `NULL` ensures the column count matches the original query.

Effect: The query returns `secret_code` values instead of normal logs.

## Challenge 4 

Click on the "forgot password" field.

Then use the following to output the password:

```
x' UNION SELECT password FROM users WHERE username='admin' --
```

What’s happening:
- The `x'` ends a string literal, assuming the original query wraps input in single quotes.
- `UNION SELECT` password pulls the admin’s password.
- `WHERE username='admin'` targets a specific user.
- `--` ignores anything after.

# Other Resources

(SQL Injection Cheat Sheet)[https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html]
