from flask import Blueprint, render_template, redirect, url_for, abort, flash
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer
from app import app, db
from app.models.security import User
from app.forms import security as user_forms
#from app.toolbox import email
from datetime import datetime

# Serializer for generating random tokens
ts = URLSafeTimedSerializer(app.config['SECRET_KEY'])


@app.route('/AAAregister', methods=['GET', 'POST'])
def signup():
    form = user_forms.ExtendedRegisterForm()
    if form.validate_on_submit():
        # Create a user who hasn't validated his email address
        # As a login, use email address from the form
        user = User(
            email=form.email.data,
            password=form.password.data#,
            #first_name=form.first_name.data,
            #last_name=form.last_name.data,
            #phone=form.phone.data,
            #locked=False,
            #active=False,
            #created_at=datetime.utcnow()
        )

        # Insert the user in the database
        db.session.add(user)
        db.session.commit()

        # Get the user from the database
        new_user = User.query.filter_by(login=form.email.data).first()

        # # Create primary user email record
        # user_email = UserEmail(
        #     user_id=new_user.id,
        #     email=form.email.data,
        #     primary=True,
        #     confirmed=False,
        #     created_at=datetime.utcnow()
        # )
        # # Add default user role
        # user_role = UserRole(
        #     user_id=user.id,
        #     role_id=1
        # )
        # db.session.add(user_email)
        # db.session.add(user_role)
        # db.session.commit()

        # Subject of the confirmation email
        subject = 'Please confirm your email address.'
        # Generate a random token
        ###token = ts.dumps(user.login, salt=app.config['EMAIL_CONFIRM_SALT'])
        # Build a confirm link with token
        ###confirmUrl = url_for('app.confirm', token=token, _external=True)
        # Render an HTML template to send by email
        ###html = render_template('email/confirm.html', confirm_url=confirmUrl)
        ###print('token confirm url: '+confirmUrl)
        # Send the email to user
        #####email.send(user_email.email, subject, html)
        # Send back to the home page
        flash('Check your emails to confirm your email address.', 'positive')
        return redirect(url_for('index'))
    return render_template('security/register_user.html', register_user_form=form)
    #return render_template('security/register_user.html', form=form, title='Register')


@app.route('/AAAconfirm/<token>', methods=['GET', 'POST'])
def confirm(token):
    try:
        email = ts.loads(token, salt=app.config['EMAIL_CONFIRM_SALT'], max_age=86400)
    # The token can either expire or be invalid
    except:
        abort(404)
    # Get the user from the database
    user = User.query.filter_by(login=email).first()
    # The user has confirmed his or her email address
    user.active = True
    ##user_email = UserEmail.query.filter_by(email=email, user_id=user.id).first()
    ##user_email.confirmed = True
    ##user_email.confirmed_at = datetime.utcnow()
    # Update the database with the user and user_email
    db.session.commit()
    # Send to the login page
    flash('Your email address has been confirmed, you can sign in.', 'positive')
    return redirect(url_for('app.login'))


@app.route('/AAAlogin', methods=['GET', 'POST'])
def login():
    form = user_forms.Login()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.email.data).first()
        # Check the user exists
        if user is not None:
            # Check the password is correct
            if user.check_password(form.password.data):
                login_user(user)
                # Send back to the home page
                flash('Succesfully logged in.', 'positive')
                return redirect(url_for('index'))
            else:
                flash('Wrong login or email address.', 'negative')
                return redirect(url_for('app.login'))
        else:
            flash('Wrong login or email address.', 'negative')
            return redirect(url_for('app.login'))
    return render_template('user/login.html', form=form, title='Login')


@app.route('/AAAsignout')
def signout():
    logout_user()
    flash('Succesfully logged out.', 'positive')
    return redirect(url_for('index'))


@app.route('/AAAaccount')
@login_required
def account():
    return render_template('user/account.html', title='Account')


@app.route('/AAAforgot', methods=['GET', 'POST'])
def forgot():
    form = user_forms.Forgot()
    if form.validate_on_submit():
        user_email = None ##UserEmail.query.filter_by(email=form.email.data, confirmed=True, primary=True).first()
        # Check the user exists
        if user_email is not None:
            # Subject of the confirmation email
            subject = 'Reset your password.'
            # Generate a random token
            ###token = ts.dumps(user_email.email, salt=app.config['EMAIL_FORGOT_SALT'])
            # Build a reset link with token
            ###resetUrl = url_for('app.reset', token=token, _external=True)
            # Render an HTML template to send by email
            html = render_template('email/reset.html', reset_url=resetUrl)
            # Send the email to user
            ###email.send(user_email.email, subject, html)
            # Send back to the home page
            flash('Check your emails to reset your password.', 'positive')
            return redirect(url_for('index'))
        else:
            flash('Unknown email address.', 'negative')
            return redirect(url_for('app.forgot'))
    return render_template('user/forgot.html', form=form)


@app.route('/AAAreset/<token>', methods=['GET', 'POST'])
def reset(token):
    try:
        email = ts.loads(token, salt=app.config['EMAIL_RESET_SALT'], max_age=86400)
    # The token can either expire or be invalid
    except:
        abort(404)
    form = user_forms.Reset()
    if form.validate_on_submit():
        user_email = None ##UserEmail.query.filter_by(email=email, confirmed=True, primary=True).first()
        user = User.query.filter_aby(user_id=user_email.user_id).first()
        # Check the user exists
        if user is not None:
            user.password = form.password.data
            # Update the database with the user
            db.session.commit()
            # Send to the login page
            flash('Your password has been reset, you can sign in.', 'positive')
            return redirect(url_for('app.login'))
        else:
            flash('Unknown email address.', 'negative')
            return redirect(url_for('app.forgot'))
    return render_template('user/reset.html', form=form, token=token)
