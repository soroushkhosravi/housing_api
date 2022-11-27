"""The definition of the flask app and it's endpoints."""
import json
import os
import requests
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
    UserMixin
)
from oauthlib.oauth2 import WebApplicationClient

from infrastructure.database import db
from models.user import User
from forms.address import AddressForm
from repositories import get_crime_repository
from datetime import datetime
from collections import defaultdict

GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['DB_URL']
app.secret_key = os.environ["SECRET_KEY"]
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "index"
client = WebApplicationClient(GOOGLE_CLIENT_ID)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/hello')
@login_required
def hello():
    """Hello mate."""
    return 'Hello matee.'


@app.route("/")
def index():
    if current_user.is_authenticated:
        return (
            "<p>Hello, {}! You're logged in! Email: {}</p>"
            "<div><p>Google Profile Picture:</p>"
            '<img src="{}" alt="Google profile pic"></img></div>'
            '<a class="button" href="/logout">Logout</a>'.format(
                current_user.name, current_user.email, current_user.profile_pic
            )
        )
    else:
        return '<a class="button" href="/login">Google Login</a>'


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # It gives us just an endpoint like the following thing:
    # authorization_endpoint:
    # https://accounts.google.com/o/oauth2/v2/auth

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    # The url is included the `fall back` route, the google client ID the scope we want:
    # request_uri:
    # https://accounts.google.com/o/oauth2/v2/auth?
    # response_type=code&
    # client_id=1039455511015-9of84all5bi5apuinop5nb02udkr02ad.apps.googleusercontent.com&
    # redirect_uri=http://127.0.0.1/5000/login/callback&
    # scope=openid+email+profile
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Token endpoint is an endpoint like the following:
    #token_endpoint:
    #  https://oauth2.googleapis.com/token

    # Prepare and send request to get tokens! Yay tokens!
    # For the following:
    #
    # request.url:
    # http://127.0.0.1:5000/login/callback?
    # code=4/0ARtbsJpaRMA653ehFkjB4AjtAp_2ibfyoMwxKswc0UsogytmMUBKeMihv1miqP2giH04uA&
    # scope=email+profile+openid+
    # https://www.googleapis.com/auth/userinfo.email+https://www.googleapis.com/auth/userinfo.profile&
    # authuser=0&
    # prompt=consent
    #
    # request.base_url:
    #  http://127.0.0.1:5000/login/callback
    #
    # code:
    # 4/0ARtbsJqnTf7LlnnK6Vz-PownqaaIzAqQWiDNM5Hs7luJZWL28Z5gCncyPTl6lyosiRIcPg

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )

    # token_url:
    #  https://oauth2.googleapis.com/token

    # headers
    # {'Content-Type': 'application/x-www-form-urlencoded'}

    # body:
    # grant_type=authorization_code&
    # client_id=1039455511015-9of84all5bi5apuinop5nb02udkr02ad.apps.googleusercontent.com&
    # code=4/0ARtbsJo5xHhbH_8ftuA_xI-kJW5RYaT1-xdyf5lZyl2kSNYKzqDTS4EVtE8L1_LE-8rDEw&
    # redirect_uri=http://127.0.0.1:5000/login/callback

    # auth: This is something that we have received from google when creating the credentials.

    # raise Exception(str(body).replace('%2F', '/').replace('%3A', ':'))
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # token_response:
    #{
    #    'access_token': 'ya29.a0Aa4xrXOo4sFLyULIWm7w5fVSIW-HCptdwz1Yw6jdDzQ34Qnyp1mXmIWROKT_V3hXg-J3jNk76UhnY4nCKUbKBxUQDaClw3m1fnJnvDeplDkMZ2cg80shM-Xn4hVws5WkHDsXTz3ouXVrACyPBNRrDNZA9gMBaCgYKATASARESFQEjDvL9VVn4rcdLgz74HJ1PQWmR3Q0163',
    #    'expires_in': 3599,
    #    'scope': 'openid https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',
    #    'token_type': 'Bearer',
    #    'id_token': 'eyJhbGciOiJSUzI1NiIsImtpZCI6ImVlMWI5Zjg4Y2ZlMzE1MWRkZDI4NGE2MWJmOGNlY2Y2NTliMTMwY2YiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiIxMDM5NDU1NTExMDE1LTlvZjg0YWxsNWJpNWFwdWlub3A1bmIwMnVka3IwMmFkLmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwiYXVkIjoiMTAzOTQ1NTUxMTAxNS05b2Y4NGFsbDViaTVhcHVpbm9wNW5iMDJ1ZGtyMDJhZC5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbSIsInN1YiI6IjExNTU2NzI5NDY2ODQ5ODQ4MzY1MCIsImVtYWlsIjoic29ydXNoLmtoNjhAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImF0X2hhc2giOiJ4YlpQd2k0elZvQUh1eUhldEN0Y0FRIiwibmFtZSI6InNvcm9vc2gga2hvc3JhdmkiLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EvQUxtNXd1MkNRb0FlSjlwZmE1R0d6dHhRcDgwOTl4MXpfT2pjaVRXcWRwbVM9czk2LWMiLCJnaXZlbl9uYW1lIjoic29yb29zaCIsImZhbWlseV9uYW1lIjoia2hvc3JhdmkiLCJsb2NhbGUiOiJlbiIsImlhdCI6MTY2NjM0NzY3MCwiZXhwIjoxNjY2MzUxMjcwfQ.lm3x3uOcjd2yAJn1EOyPuNH9ILKMGkYH_u7XzIFJ3uGby61sCj4THFhbZmajHoa4157XufBLLub6VuqQR0qbVJKce1vhIELIQIbN7fUm0thg8q7Za2FY40h4Iikyd208qHAUMf0o-fe7q30sg3CfsJn25kcXIaS5kCM9iqb_pEbEYuigK43O1siTLq1bJNIgfmjZFJJQByRj9a2ayfKOEtqEfztW955MUDhIEFjJFa1TolBYTW1Wxddo7TtMBCQKUm9tAvlx5b_qI3Ui_LpwgTK2eJ6xBmuhzyF-kkF28XNdAZ7fYTvG5Mu_XH-DMNzl78laWgp4pEqbSe22BKelgw'
    # }

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)

    # uri:
    #  https://openidconnect.googleapis.com/v1/userinfo

    # headers:
    # {'Authorization':
    # 'Bearer ya29.a0Aa4xrXNNnuGPAjlEdvJ3_HlW6NhcXJiWCqLYQ-n-1JFK898_p1Ai7_px3p4wsjrFm4Das-cm9TjoQZv0BVvRhnZLWmNwnBt
    # HEvYemIdbBfiO6wujl0mxlzGub0okia4JS6jzie_qTQaVlJ_lbzvjZnRh4q4VaCgYKATASARISFQEjDvL9WAcpXM2m6RYZULPDmiG4Og0163'
    # }
    # body:
    # None
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in our db with the information provided
    # by Google
    # user = User(
    #     id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    # )

    # Doesn't exist? Add to database
    existing_user = User.query.get(unique_id)
    if not existing_user:
        user = User(id=unique_id, name=users_name, email=users_email, profile_pic=picture)
        db.session.add(user)
        db.session.commit()
        existing_user = user

    # raise Exception(existing_user.id)
    # Begin user session by logging the user in
    login_user(existing_user)

    # Send user back to homepage
    return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route('/address', methods=["GET", "POST"])
def investigate_address():
    """Investigates a specific address."""
    form = AddressForm()
    if form.validate_on_submit():
        crimes = get_crime_repository().get_crimes(
            postcode=form.post_code.data,
            month=datetime.now().month - 2,
            year=datetime.now().year
        )

        crimes_dict = defaultdict(lambda: 0) if crimes else {}

        for crime in crimes:
            crimes_dict[crime.category] += 1

        return render_template('crimes.html', crimes=crimes_dict)

    return render_template('address_form.html', form=form)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()