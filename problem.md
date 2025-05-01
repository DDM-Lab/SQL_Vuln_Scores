# SQL_VULN_SCORES

- Namespace: picoctf/research
- ID: sqli-scores-treatment
- Type: custom
- Category: Web Exploitation
- Points: 1
- Templatable: yes
- MaxUsers: 1

## Description

There are various endpoints vulnerable to SQL Injection. You only need to exploit one of them.

**NOTE: Do not close the Qualtrics survey.**

## Details

Browse {{link_as('/', 'here')}}, and find the flag!

**NOTE: Do not forget to download the Qualtrics data (`sql_challenge.txt`) along with the flag!**

## Hints

- Look at the hints on the Home page
- You can use the walkthrough provided in the Qualtrics survey.

## Solution Overview

Figure out the DB structure, appropriate table and retrieve the flag.

## Challenge Options

```yaml
cpus: 0.5
memory: 128m
pidslimit: 20
ulimits:
  - nofile=128:128
diskquota: 64m
init: true
```

## Learning Objective

Understand SQL Injection

## Tags

- web

## Attributes

- author: DDM Lab
- organization: picoCTF
- event: picoCTF Experimental Problems 1
