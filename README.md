## Python Flask Skeleton for Google App Engine

A skeleton for building Python applications on Google App Engine with the
[Flask micro framework](http://flask.pocoo.org).

## Run Locally
1. Install the [App Engine Python SDK](https://developers.google.com/appengine/downloads).
See the README file for directions. You'll need python 2.7 and [pip 1.4 or later](http://www.pip-installer.org/en/latest/installing.html) installed too.

2. Clone this repo with

   ```
   git clone git@bitbucket.org:aukbit/apollo.git
   ```

2 Virtual environment

2.1 Create virtual environment

   ```
   virtualenv ~/.virtualenv/apollo
   ```

2.2 Activate virtual environment

   ```
   source ~/.virtualenv/apollo/bin/activate
   ```

2.3 Install dependencies

   ```
   pip install -r requirements.txt
   ```

3. Install dependencies in the project's lib directory.
   Note: App Engine can only import libraries from inside your project directory.

   ```
   mkdir lib
   pip install -r requirements.txt -t lib
   ```
4. Run this project locally from the command line:

   ```
   bash run_server.sh
   ```

Visit the application [http://localhost:8080](http://localhost:8080)

See [the development server documentation](https://developers.google.com/appengine/docs/python/tools/devserver)
for options when running dev_appserver.
