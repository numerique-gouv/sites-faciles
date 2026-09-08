# Scalingo review apps

Created from the Scalingo dashboard (parent app → Review apps → Manual
deployment).

`scalingo.json` sets hostnames and a fresh a sandbox Postgres addon.
create_starter_content is run so the review app should have demo pages.

Note : the review apps are created with `DISABLE_COLLECTSTATIC=1` (the Python
buildpack skips `collectstatic` at compile time) because `DATABASE_URL` is not
available yet at build time. Then `scripts/scalingo/web.sh` and
`just scalingo-postdeploy` run `collectstatic` once addon env vars exist.

## Admin account

Postdeploy does **not** create a superuser. After the review app is up:

```bash
scalingo --app <review-app-name> --region osc-fr1 run python manage.py createsuperuser
```

Then sign in at `/cms-admin/` with that username and password.
