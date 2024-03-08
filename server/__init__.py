from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from datetime import timedelta
from flask_jwt_extended import JWTManager
from flask_mail import Mail


app = Flask(__name__)

app.config['MAIL_SERVER'] = 'mail.privateemail.com'  # Replace with your SMTP server
app.config['MAIL_PORT'] = 587  # Replace with your SMTP server port
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'no-reply@mystudays.com'  # Replace with your email username
app.config['MAIL_PASSWORD'] = 'StudaysPassword2024'  # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = 'no-reply@mystudays.com'

mail = Mail(app)


username = "4rlba1yq1uo8f7ozvdfk"
password = "pscale_pw_esEiq6xj2zXKckMACmOeuBUEHfsEPVO9cHyFtZSdpW6"
hostname = "aws.connect.psdb.cloud"
database = "studays"

app.config['JWT_SECRET_KEY'] = 'studays_vol_!!@'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=364)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config["UPLOADED_PHOTOS_DEST"] = "uploaded_images"


Swagger(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)

from server.controller import routes
