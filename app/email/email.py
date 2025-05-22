from flask import render_template, url_for, current_app
from flask_mail import Message
from app import mail
from threading import Thread

def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipients, template, **kwargs):
    """Generic email sender"""
    msg = Message(subject, recipients=recipients)
    msg.html = render_template(template, **kwargs)
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_confirmation_email(user, pendaftaran):
    """Send registration confirmation email"""
    send_email(
        'Konfirmasi Pendaftaran PPDB SMK Karya Bangsa',
        recipients=[user.email],
        template='email/confirmation.html',
        user=user,
        pendaftaran=pendaftaran
    )

def send_reset_password_email(user, token):
    """Send password reset email"""
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    send_email(
        'Reset Password PPDB SMK Karya Bangsa',
        recipients=[user.email],
        template='email/reset_password.html',
        user=user,
        reset_url=reset_url
    )

def send_verification_email(user, token):
    """Send email verification email"""
    verification_url = url_for('auth.verify_email', token=token, _external=True)
    send_email(
        'Verifikasi Email PPDB SMK Karya Bangsa',
        recipients=[user.email],
        template='email/verification.html',
        user=user,
        verification_url=verification_url
    )