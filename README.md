Flask Skeleton
--------------
A full flask project skeleton built on bootstrap.  
Features include:
- User login
- Role based access control
- An example page
- An example form
- 404 and 500 error handling
- Admin panel for users and roles
- sqlite backend with mysql support in a few line changes (via SQLAlchemy)
- Comments so you can figure out how stuff works

To start using, simply:
```
# git clone --recursive https://github.com/jgeigerm/flask-examples
# cd flask-examples/skeleton
# virtualenv flask
# source flask/bin/activate
# pip install -r requirements.txt
# ./run.py
```
If you are actually using this as a skeleton, change the name, content, and most importantly the information within [app.vars](./app.vars) . It contains an initial user's login credentials, the secret key for the app, and the password salt so change them or you're gonna have a bad time. You can look in [config.py](./config.py) to find out what variables are read from which lines in the [app.vars](./app.vars) file.

run.py can be used with arguments to change the port, debug mode, and bind address:
```
# ./run.py -d
# ./run.py -d -p 50000
# ./run.py -b 0.0.0.0 -p 80
```
The defaults are: debug:False, port:8080, bind:127.0.0.1

If you have any questions about the functionality or why something works (if the comments aren't enough) feel free to reach out to me. Enjoy.
