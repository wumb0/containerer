#!flask/bin/python
from app import db, app, docker_client
from flask import render_template, g, Blueprint
from flask_security import current_user, login_required
from app.crypto import generate_keypair
from app.models import *
from app.forms import *
import socket
from contextlib import closing

def _find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

# create a blueprint called main
main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
@main.route('/home')
def index():
    return render_template("index.html")

@main.route('/startcontainer')
def start_container():
    privkey, pubkey = generate_keypair()
    c = ContainerInstance(privkey=privkey, pubkey=pubkey)
    db.session.add(c)
    db.session.commit()
    env = {"CONFIG_USERNAME": c.username, "CONFIG_SSHKEY": pubkey}
    container = docker_client.containers.run(app.config['CONTAINER_NAME'],
                                             detach=True,
                                             environment=env,
                                             ports={"22/tcp": None})

    port = docker_client.api.inspect_container(container.id)["NetworkSettings"]["Ports"]["22/tcp"][0]['HostPort']
    c.hash = container.id
    c.port = port
    db.session.add(c)
    db.session.commit()

@main.route('/examplepage')
@login_required
def examplepage():
    return render_template('examplepage.html', title="Example Page!")

@main.route('/exampleform', methods=['GET', 'POST'])
@login_required
def exampleform():
    form = ExampleForm()
    form.user.choices = [ (x.email, x.email) for x in User.query.all() ]
    if form.validate_on_submit():
        flash("Good job you filled out the form: {}, {}, {}, {}".format(form.user.data,
                                                                         form.anumber.data,
                                                                         form.text.data,
                                                                         form.checkbox.data),
              category="good")
    else:
        form.flash_errors()
    return render_template("exampleform.html", title="Example Form!", form=form)


@main.route('/break')
def breakit():
    raise Exception
