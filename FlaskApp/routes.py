from flask import Flask, render_template, url_for, flash, redirect, jsonify, request
from FlaskApp import app, config
from FlaskApp.forms import LoginForm
from flask_login import current_user, logout_user,login_required
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import WebApplicationClient
import jwt, requests, json, datetime


client = WebApplicationClient(config.GOOGLE_CLIENT_ID)


@app.route("/about")
def about():
    return render_template('about.html', title='About')



@app.route("/", methods=['GET', 'POST'])
@app.route("/login_home", methods=['GET', 'POST'])
def login_home():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@app.com' and form.password.data == 'password':
        	token = jwt.encode({'user' : form.email.data, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds = 30)},app.config['SECRET_KEY'])
        	return jsonify({'token' : token.decode('UTF-8')}) 
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form) 



@app.route("/login")
def login():
    google_provider_cfg = requests.get(config.GOOGLE_LOGIN_BUILD_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=config.REDIRECT_URI,
        scope=["openid", "email"],
    )
    return redirect(request_uri)



@app.route("/login/callback")
def callback():
    code = request.args.get("code")
    google_provider_cfg = requests.get(config.GOOGLE_LOGIN_BUILD_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(config.GOOGLE_CLIENT_ID, config.GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        user_id = userinfo_response.json()['sub']
        token = jwt.encode({'user' : user_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds = 30)},app.config['SECRET_KEY'])
        return jsonify({'token' : token.decode('UTF-8')})
    else:
        return "Unable to verify User by Google.", 400


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out!', 'danger')
    return render_template('about.html', title='About')        