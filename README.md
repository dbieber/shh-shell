# Welcome to the shh-shell.

## Installation

git clone https://github.com/dbieber/shh-shell

## Dependencies

pip install -r requirements.txt

Install redis: `brew install redis`

## Setup

cp settings/secure_settings_template.py settings/secure_settings.py

Then, edit settings/secure_settings.py with your settings.

### Required settings:

**LOG_DIR**: The directory to save keylogs to.

**TEXT_DIR**: The directory to save text files to.

### Optional settings:

**DEFAULT_EMAIL**: The email address to send emails from.

**DEFAULT_EMAIL_RECIPIENT**: The email address to send emails to.

**DEFAULT_SERVICE**: The Mac Automator service to use for sending text messages / iMessages.

## Starting the shh-shell

First, start a redis-server.

`redis-server`

Then, start shh-shell by running app.py.

`python app.py`

## Using the shh-shell

tl;dr Type in the shh-shell window with your eyes closed and monitor off.

More detailed instructions for using the shh-shell are available at [davidbieber.com/projects/shh-shell](https://davidbieber.com/projects/shh-shell).
