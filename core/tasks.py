from __future__ import absolute_import, unicode_literals

from compressed_image.celery import app
from core.utils import send_email


@app.task
def send_email_bg(msg, subject, emails):
    send_email(msg, subject, emails)

