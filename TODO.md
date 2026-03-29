# MapSearch.app — TODO

## Email Setup (Cloudflare DNS + cPanel Hosting)

- [ ] **Create email account in cPanel** — Log into cPanel, go to Email Accounts, create `noreply@mapsearch.app`. Note the password and SMTP server hostname (check Connect Devices section).
- [ ] **Add MX + mail A record in Cloudflare** — DNS → add MX record: `@` → `mail.mapsearch.app`, priority 10. Add A record: `mail` → shared hosting IP, **DNS only** (grey cloud, no proxy).
- [ ] **Add SPF + DKIM + DMARC records in Cloudflare** — TXT `@` → `v=spf1 a mx include:_spf.your-host.com ~all` (check hosting provider for exact include). DKIM: get from cPanel → Email Deliverability. TXT `_dmarc` → `v=DMARC1; p=none; rua=mailto:noreply@mapsearch.app`.
- [ ] **Set email routing to Local in cPanel** — cPanel → Email Routing → set to Local Mail Exchanger (not remote or auto-detect).
- [ ] **Configure SMTP env vars on VPS** — Set in `.env` on VPS (82.21.4.94): `SMTP_HOST`, `SMTP_PORT` (465 or 587), `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`. If port 465, update `email_service.py` to use `SMTP_SSL` instead of `SMTP` + `starttls()`.
- [ ] **Verify email deliverability** — Wait ~5 min for DNS propagation. Check cPanel → Email Deliverability for green SPF/DKIM. Trigger a password reset to test end-to-end. Check email doesn't land in spam.

## Pre-Launch

- [ ] Email confirmation on signup (extend `email_service.py`, add `email_verified` column)
- [ ] Production error logging/monitoring (Sentry or structured JSON logging)
