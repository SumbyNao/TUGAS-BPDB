from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.auth import auth_bp
from app.auth.forms import LoginForm, RegisterForm
from app.models import User

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        flash('Email atau password salah.', 'danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            nama_lengkap=form.nama_lengkap.data,
            email=form.email.data.lower()
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))