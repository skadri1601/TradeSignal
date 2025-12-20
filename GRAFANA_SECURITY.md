# Grafana Security Configuration

## Default Password

The default Grafana admin password is set via `GRAFANA_ADMIN_PASSWORD` environment variable.

### Setup

1. Add to your `.env` file:
```env
GRAFANA_ADMIN_PASSWORD=your_strong_password_here
```

2. Generate a strong password:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

3. On first login, change the admin password immediately

## Access Control

- Admin interface: http://localhost:3500 (or configured port)
- Default username: `admin`
- Default password: From `GRAFANA_ADMIN_PASSWORD` env var

## Production Checklist

- [ ] Strong admin password set (min 20 characters)
- [ ] User sign-up disabled (`GF_USERS_ALLOW_SIGN_UP=false`)
- [ ] HTTPS enabled for external access
- [ ] Network access restricted (firewall rules)
