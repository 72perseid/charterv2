# ADR 0010: Django session auth with email as the username

Date: 2026-09-08. Status: accepted.

Nothing to add: `contrib.auth` with a custom user whose login is the email, session cookies, CSRF header on unsafe methods. Email verification is a setting that switches on when SMTP is configured; until then registration is open with rate limits.
