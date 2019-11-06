#!flask/bin/python
from app import db, app, docker_client, sched
from flask import render_template, g, Blueprint, jsonify
from flask_security import current_user, login_required
from datetime import timedelta
from app.crypto import generate_keypair
from app.models import *
from app.forms import *

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
    c.job_id = sched.enqueue_in(timedelta(minutes=1), expire_container, c.id)
    db.session.merge(c)
    db.session.commit()
    return '{"status": "OK"}', 200

def expire_container(id):
    c = ContainerInstance.query.one_or_none(id)
    if not c:
        return
    cont = docker_client.containers.get(c.id)
    cont.kill()
    cont.remove()
    db.session.remove(c)
    db.session.commit()


@main.route('/getcreds/<int:id>')
def get_creds(id):
    c = ContainerInstance.query.get_or_404(id)
    d = {"privkey": c.privkey.decode(), "pubkey": c.pubkey.decode(), "port": c.port, "hash": c.hash, "username": c.username}
    print(d)
    return jsonify(d)

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
