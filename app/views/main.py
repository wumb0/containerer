#!flask/bin/python
from app import db, app, docker_client, sched
from flask import render_template, g, Blueprint, jsonify, session, request, Response
from flask_security import current_user, login_required
from datetime import timedelta, datetime
from app.crypto import generate_keypair
from app.util import schedule_expiry, expire_container, is_running
from app.models import *
import socket

# create a blueprint called main
main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
@main.route('/home')
def index():
    c = None
    if 'container' in session:
        c = ContainerInstance.query.filter_by(hash=session['container']).one_or_none()
    return render_template("index.html", container=c, host=socket.gethostname(), containername=app.config["CONTAINER_NAME"])

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
    c.extends = app.config['USER_EXTENDS']
    schedule_expiry(c)
    session['container'] = c.hash
    ret = {"status": "SUCCESS"}
    return jsonify(ret)

@main.route('/getcreds/<hash>')
def get_creds(hash):
    c = ContainerInstance.query.filter_by(hash=hash).first_or_404()
    d = {"privkey": c.privkey, "pubkey": c.pubkey, "port": c.port, "hash": c.hash, "username": c.username}
    return jsonify(d), 200

@main.route('/expire/<hash>')
def expire(hash):
    c = ContainerInstance.query.filter_by(hash=hash).first_or_404()
    expire_container(c.id)
    if 'container' in session:
        del session['container']
    ret = {"status": "SUCCESS"}
    return jsonify(ret), 200

@main.route('/getkey/<hash>')
def get_key(hash):
    c = ContainerInstance.query.filter_by(hash=hash).first_or_404()
    fn = "{}-{}-{}.pem".format(c.username, request.host.split(":")[0], c.port)
    return Response(
        c.privkey,
        mimetype="application/x-pem-file",
        headers={"Content-disposition":
                 "attachment; filename="+fn})

@main.route('/extend/<hash>')
def extend(hash):
    c = ContainerInstance.query.filter_by(hash=hash).first_or_404()
    if c.extends > 0:
        sched.cancel(c.job_id)
        c.extends -= 1
        schedule_expiry(c)
        return jsonify({"status": "SUCCESS"}), 200
    else:
        return jsonify({"status": "FAILURE"}), 401
