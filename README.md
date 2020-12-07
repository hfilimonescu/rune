# Rune

A framework based on Flask with auth, translations, celery and mail

Also, a sign of the script used by the Germans. [More](https://en.wikipedia.org/wiki/Runes)

# Installation Instructions

I prefere to use virtual environments to keep everything clean and tidy. You can skip this step if you prefere it another way.
You can also use other packages to create your virtual environment.

## 0. TL;DR

``` bash
$ python3 -m venv venv --prompt rune
$ source venv/bin/activate
(rune) $ pip install -U pip wheel rune
(rune) $ flask core init -d
(rune) $ flask db init
(rune) $ flask db migrate
(rune) $ flask db upgrade
(rune) $ flask auth create-admins
(rune) $ flask run
```

http://localhost:5000

Username: rune

Password: RUNE


## 1. Create a virtualenv

``` bash
$ python3 -m venv venv --prompt rune
$ source venv/bin/activate
```

### 1.a. Optionally update `pip` and `wheel`

``` bash
(rune) $ pip install -U pip wheel
Collecting pip
  Using cached pip-20.3.1-py2.py3-none-any.whl (1.5 MB)
Collecting wheel
  Downloading wheel-0.36.1-py2.py3-none-any.whl (34 kB)
Installing collected packages: pip, wheel
  Attempting uninstall: pip
    Found existing installation: pip 20.0.2
    Uninstalling pip-20.0.2:
      Successfully uninstalled pip-20.0.2
Successfully installed pip-20.3.1 wheel-0.36.1
```

## 2. Install Rune and it's dependencies using `pip`

``` bash
(rune) $ pip install rune
```

## 3. Set up the required boilerplate

Rune provides two command groups, that help you set up the applications quicker.

The first one is `flask core init`, with which you can create the config files to run the application.

The second one is `flask auth create-ddic`, which creates the `ddic` (dedicated) user.

``` bash
(rune) $ flask --help

  A general utility script for Flask applications.

  Provides commands from Flask, extensions, and the application. Loads the
  application defined in the FLASK_APP environment variable, or from a
  wsgi.py file. Setting the FLASK_ENV environment variable to 'development'
  will enable debug mode.

    $ export FLASK_APP=hello.py
    $ export FLASK_ENV=development
    $ flask run

Options:
  --version  Show the flask version
  --help     Show this message and exit.

Commands:
  auth    Rune A12n and A11n commands   <-- Rune Auth commands
  core    Rune Core commands            <-- Rune core commands
  db      Perform database migrations.
  routes  Show the routes for the app.
  run     Run a development server.
  shell   Run a shell in the app context.

```

### 3.1. Create the config files `.env`, `.flaskenv`, and `rune.conf`

The command `flask core init` has two optional flags to create configuration for `development` or `testing` purposes.

If no flag is passed it will create the configuration files for production.

``` bash
(rune) $ flask core init --help
Usage: flask core init [OPTIONS]

  Create the initial env files to run Rune in production

Options:
  -t, --testing      Config for testing purposes
  -d, --development  Config for development purposes
  --help             Show this message and exit.
```

In this case we want to use the `-d` flag:

``` bash
(rune) $ flask core init -d
Write to dev_rune.conf
Write to .env
Write to .flaskenv
```

### 3.2. Review the configuration

Review the newly created files and adjust them accordingly. The most important config keys, in the `rune.conf` file, you need to modify are:

- `SQLALCHEMY_DATABASE_URI`
- `RUNE_ADMINS`
- `MAIL_SERVER`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`

`RUNE_ADMINS` will be used to create the first admin accounts.
This users have super powers, as they will always have all permissions (installed or not) checked by the application.

## 4. Set Up the Database Migrations

``` bash
(rune) $ flask db init
  Creating directory /home/xx/rune/migrations ...  done
  Creating directory /home/xx/rune/migrations/versions ...  done
  Generating /home/xx/rune/migrations/script.py.mako ...  done
  Generating /home/xx/rune/migrations/env.py ...  done
  Generating /home/xx/rune/migrations/alembic.ini ...  done
  Generating /home/xx/rune/migrations/README ...  done
  Please edit configuration/connection/logging settings in '/home/xx/rune/migrations/alembic.ini' before proceeding.
```

``` bash
(rune) $ flask db migrate -m "Initial migration"
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'auth_permissions'
INFO  [alembic.autogenerate.compare] Detected added table 'auth_roles'
INFO  [alembic.autogenerate.compare] Detected added table 'auth_users'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_auth_users_email' on '['email']'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_auth_users_token' on '['token']'
INFO  [alembic.autogenerate.compare] Detected added table 'auth_role_permissions'
INFO  [alembic.autogenerate.compare] Detected added table 'auth_user_preferences'
INFO  [alembic.autogenerate.compare] Detected added table 'auth_user_roles'
INFO  [alembic.autogenerate.compare] Detected added table 'main_messages'
  Generating /home/xx/rune/migrations/versions/3d2efd9a5a07_initial_migration.py ...  done
```

``` bash
(rune) $ flask db upgrade
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 3d2efd9a5a07, Initial migration
```

## 5. Create the Admin / Dedicated User

The tool creates the admin accounts as defined in the config file under te key `RUNE_ADMINS`.

Username is always set to the username part of the email address.

Password is always set to `RUNE` initially.

__IMPORTANT!__: On the first login you will be prompted to change it.

``` bash
(rune) $ flask auth create-admins
Creating user rune@example.com...
Created user rune@example.com.
```

## 6. Run the Application

``` bash
(rune) $ flask run
 * Serving Flask app "rune.wsgi" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 000-000-000
```

### 7. Log In and Browse

http://localhost:5000

Username: rune

Password: RUNE
