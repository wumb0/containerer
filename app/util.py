from app import app, sched, docker_client, db
from app.models import ContainerInstance
from datetime import datetime, timedelta

def schedule_expiry(c):
    c.expiry = datetime.utcnow() + timedelta(minutes=app.config['EXPIRE_TIME'])
    c.job_id = sched.enqueue_at(c.expiry, expire_container, c.id).id
    db.session.merge(c)
    db.session.commit()

def expire_container(id):
    with app.app_context():
        c = ContainerInstance.query.get(id)
        if not c:
            return
        cont = docker_client.containers.get(c.hash)
        cont.kill()
        cont.remove()
        if c.job_id in sched:
            sched.cancel(c.job_id)
        db.session.delete(c)
        db.session.commit()
        db.session.flush()

def is_running(ch):
    cont = docker_client.containers.get(ch)
    return cont.status == 'running'

