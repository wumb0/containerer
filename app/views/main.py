#!flask/bin/python
from app import db, app, docker_client, sched
from flask import render_template, g, Blueprint, jsonify, session
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
    return render_template("index.html", containers=session['container'])

@main.route('/startcontainer')
def start_container():
    if 'container' in session:
        c = ContainerInstance.query.filter_by(hash=session['container']).one_or_none()
        if c != None and is_running(c.hash):
            ret = {"status": "FAILURE"}
            return jsonify(ret), 401
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
    c.job_id = sched.enqueue_in(timedelta(minutes=app.config['EXPIRE_TIME']), expire_container, c.id).id
    db.session.merge(c)
    db.session.commit()
    session['container'] = c.hash
    ret = {"status": "SUCCESS"}
    return jsonify(ret)

def expire_container(id):
    with app.app_context():
        c = ContainerInstance.query.get(id)
        if not c:
            return
        cont = docker_client.containers.get(c.hash)
        cont.kill()
        cont.remove()
        db.session.delete(c)
        db.session.commit()

def is_running(ch):
    cont = docker_client.containers.get(ch)
    return cont.status == 'running'

@main.route('/getcreds/<int:id>')
def get_creds(id):
    c = ContainerInstance.query.get_or_404(id)
    d = {"privkey": c.privkey.decode(), "pubkey": c.pubkey.decode(), "port": c.port, "hash": c.hash, "username": c.username}
    return jsonify(d)

@main.route('/expire/<int:id>')
def expire(id):
    expire_container(id)
    if 'container' in session:
        del session['container']
