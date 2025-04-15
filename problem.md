# Web CSS

- Namespace: picoctf/research
- ID: sqli-scores
- Type: custom
- Category: Web Exploitation
- Points: 1
- Templatable: yes
- MaxUsers: 1

## Description

There are various endpoints vulnerable to SQL Injection. Can you exploit them?

## Details

Browse {{link_as('/', 'here')}}, and find the flag!

## Hints

- Look at the hints on the Home page

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
- event: DDM LAB Research