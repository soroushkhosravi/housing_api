"""The definition of the flask app and it's endpoints."""
import json
import os
import requests
from collections import defaultdict
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template, request, redirect, url_for, make_response, abort, session
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
    UserMixin
)
from forms.address import AddressForm
from infrastructure.database import db
from models.user import User, MyAnonymousUser
from oauthlib.oauth2 import WebApplicationClient
from repositories import get_crime_repository, get_user_repository
from services import get_user_service
import redis
import jwt
import logging
from flask_cors import CORS

GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['DB_URL']
app.secret_key = os.environ["SECRET_KEY"]
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

# This is coomented out as we have unauthorised auth handler.
# login_manager.login_view = "index"
login_manager.anonymous_user = MyAnonymousUser
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# redis_for_app = redis.Redis(
#     host=os.environ["REDIS_HOST"],
#     port=os.environ["REDIS_PORT"]
# )

# Change this to an env variable coming from the AWS and inject it to the deployment containers.
JWT_SECRET = 'SOROUSH'
JWT_VALID_EXPIRY_SECONDS = 100
JWT_ALGORITHM = 'HS256'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorised():
    """Handling the login process properly."""
    if request.path.split('/')[1] == 'api':
        return jsonify({
            "message": "user not logged in.",
            "auth_url": request.url_root + '/login'
        })
    return redirect(url_for('index'))


@login_manager.request_loader
def load_user_from_request(request):
    """Loads the user from request.

    By using this function, you will be able to grab the user from the request, sessions, cookies, etc.

    It is another option like the user_loader which reads the user from the flask session set by login_user function.
    """
    user = None

    jwt_token = request.cookies.get('jwt_token')
    if not jwt_token:
        headers = request.headers
        if headers.get('Authentication'):
            authentication = headers['Authentication']
            split_header = authentication.split(' ')
            if len(split_header) != 2 or split_header[0] != 'Bearer':
                return user
            jwt_token = split_header[1]
    if jwt_token:
        try:
            google_id = jwt.decode(jwt_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

            google_id = google_id.get('google_id')
            if google_id:

                user = get_user_repository().get_by_google_id(google_id=google_id)

        except (jwt.DecodeError, jwt.ExpiredSignatureError):
            pass
    return user

@app.route('/api')
@login_required
def api():
    """Hello mate. this is hello."""
    logging.error('An error happened!')
    return f'Hello mate. You are my friend.'

@app.route('/user')
@login_required
def get_user():
    """Getting the current user."""
    return jsonify(name=current_user.name)


@app.route("/")
def index():
    return render_template(
        'index.html'
    ) if current_user.is_authenticated else '<a class="button" href="/login">Google Login</a>'


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    # google_provider_cfg = get_google_provider_cfg()
    # authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # It gives us just an endpoint like the following thing:
    # authorization_endpoint:
    # https://accounts.google.com/o/oauth2/v2/auth

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google

    # The following piece of code can be used to get the separate frontend url when calling login function from outside
    # like a complete react frontend and in the /callback, we can redirect to that url.
    next_url = request.args.get('next_url')
    session['next_url'] = next_url
    request_uri = client.prepare_request_uri(
        get_google_provider_cfg()["authorization_endpoint"],
        redirect_uri=request.base_url + f"/callback",
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
    # code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()

    # Token endpoint is an endpoint like the following:
    # token_endpoint:
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
        google_provider_cfg["token_endpoint"],
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=request.args.get("code"),
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
    # {
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
    existing_user = get_user_service().existing_google_user(
        unique_google_id=unique_id,
        email=users_email,
        picture=picture,
        username=users_name
    )

    # This function puts the user_id in the session which is a cookie named session.
    # And the user will be read by the user_loader function.
    # login_user(existing_user)
    jwt_token = jwt.encode(
        {
            'google_id': existing_user.google_id,
            'exp': datetime.utcnow() + timedelta(seconds=JWT_VALID_EXPIRY_SECONDS)
        },
        JWT_SECRET,
        JWT_ALGORITHM
    )

    if session.get('next_url') is None:
        response = make_response(redirect(url_for("index")))
        # The token is set to enable us use the request loader function.
        # If we want to set a cross site cookie, we use the following code:
        # esp.headers.add('Set-Cookie','cross-site-cookie=bar; SameSite=None; Secure')
        response.set_cookie('jwt_token', jwt_token, httponly=True)
        return response

    # This part of code can be used if we have a separate frontend to redirect to it.
    # We get the url in the login function.
    ext_domain = f"{session['next_url']}" + f"/{jwt_token}"
    return redirect(ext_domain)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    response = make_response(redirect(url_for("index")))
    response.delete_cookie('jwt_token')
    return response

@app.route("/raise")
def raise_exception():
    """Raises an exception."""
    raise Exception("An error is raised. Can you see in datadog?")

@app.route('/redis/<name>')
def redis_setting(name):
    """."""
    # redis_for_app.set('name', name)

    return 'Name Set successfully. Yeah.'

@app.route('/name')
def get_name():
    # name = redis_for_app.get('name')
    return 'name'

@app.route('/ip-show')
def show_ip():
    """Shows the ip of the request sender of the request."""
    return jsonify({'ip': request.environ.get('HTTP_X_REAL_IP', request.remote_addr)})

@app.route('/address', methods=["GET", "POST"])
@login_required
def investigate_address():
    """Investigates a specific address.."""
    form = AddressForm()

    rendering_template = render_template('address_form.html', form=form, user=current_user)

    if form.validate_on_submit():
        three_month_earlier = datetime.now() - timedelta(days=90)
        crimes = get_crime_repository().get_crimes(
            postcode=form.post_code.data,
            month=three_month_earlier.month,
            year=three_month_earlier.year
        )

        crimes_dict = defaultdict(lambda: 0) if crimes else {}

        for crime in crimes:
            crimes_dict[crime.category] += 1

        rendering_template = render_template('crimes.html', crimes=crimes_dict, crimes_number=len(crimes))

    return rendering_template

@app.route("/api/user")
@login_required
def user():
    """Returns the data of a current users."""
    return jsonify({
        "message": "current user is found.",
        "user": json.dumps({"username": current_user.name, "email": current_user.email})
    })

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()
