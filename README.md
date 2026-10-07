# SWE1 Django polls

A small polls application based on parts 1-4 of the [official Django tutorial](https://docs.djangoproject.com/en/6.1/intro/tutorial01/).

Users can open a question, select an answer, submit a vote, and see the vote totals. Questions and choices can also be managed through Django's admin site.

## Run locally

Use Python 3.12.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_polls
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/polls/`. The admin site is at `http://127.0.0.1:8000/admin/`.

The sample-data command can be run again without resetting votes. For new questions, use the admin site or edit `polls/management/commands/seed_polls.py` before the first deployment.

## Project files

| File | Purpose |
| --- | --- |
| `polls/models.py` | Question and Choice database models |
| `polls/migrations/0001_initial.py` | Database schema migration |
| `polls/urls.py` | Named routes for listing, details, voting, and results |
| `polls/views.py` | Generic views and the POST voting handler |
| `polls/templates/polls/` | HTML pages and the voting form |
| `polls/admin.py` | Registers the models in Django admin |
| `mysite/settings.py` | Local and deployed environment settings |
| `.ebextensions/django.config` | WSGI, environment variables, and static files for AWS |
| `.platform/hooks/predeploy/01_prepare_app.sh` | Migrations, initial questions, and static collection |

The small additions beyond parts 1-4 are a home-page redirect, shared HTML template, sample-data command, checks for future questions, POST-only voting, and tests. The app intentionally uses the basic tutorial interface.

## Tests

```bash
python manage.py check
python manage.py test
```

Tests cover the voting flow, repeated results-page refreshes, invalid choices, unpublished questions, and safe repeated sample-data setup.

## Elastic Beanstalk

Choose the Python 3.12 platform on Amazon Linux 2023 and a **single-instance** environment. The platform supplies Gunicorn; the WSGI entry point is `mysite.wsgi:application`.

Set `DJANGO_SECRET_KEY` as an Elastic Beanstalk environment property before the first deployment. The packaged configuration sets `DJANGO_DEBUG=false`, and the application refuses to start in that mode without a secret key.

Once AWS assigns a domain, set `DJANGO_ALLOWED_HOSTS` to that exact hostname, plus `localhost,127.0.0.1` for local health requests. Do not include a scheme or `/polls/` in that setting.

The deployment hook migrates the database, adds sample questions, and collects static files automatically. Do not upload your local database, virtual environment, credentials, or private keys.

### Database limitation

The deployed SQLite database is `/var/app/data/db.sqlite3`, outside the application release directory. It remains during normal deployments on the same EC2 instance. It is still instance-local: replacing or terminating the instance can lose votes and admin accounts. A replacement instance receives the sample questions again. Use an external database such as RDS PostgreSQL if persistent data or multiple instances become a requirement.

This minimal setup serves HTTP. Configuring HTTPS is a separate hosting step; use the actual working protocol in the submission URL. Admin accounts created on your laptop are local and are not uploaded.

## References

- [Django tutorial, part 1](https://docs.djangoproject.com/en/6.1/intro/tutorial01/)
- [Django tutorial, part 2](https://docs.djangoproject.com/en/6.1/intro/tutorial02/)
- [Django tutorial, part 3](https://docs.djangoproject.com/en/6.1/intro/tutorial03/)
- [Django tutorial, part 4](https://docs.djangoproject.com/en/6.1/intro/tutorial04/)
- [AWS Django deployment guide](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-django.html)
- [AWS platform hooks](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/platforms-linux-extend.hooks.html)
