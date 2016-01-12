# -*- coding:utf-8 -*-

from flask import render_template, session, redirect, url_for, request, flash
from flask.ext.login import login_user, logout_user, login_required, current_user
from . import auth
from .forms import LoginForm, RegistrationForm
from ..models import User
from .. import db
from ..email import send_email
from ..decorators import admin_required, permission_required


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash(u'welcome, %s' % user.username)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/rigister', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate():
        user = User(email=form.email.data, \
                    username=form.username.data, \
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'confirm',
                   'auth/email/confirm', user=user, token=token)
        flash(u'A confirmation email has been sent to you by email.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
        and not current_user.confirmed \
        and request.endpoint[:5] != 'auth.':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash(u'A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))