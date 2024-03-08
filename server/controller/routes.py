from flask import jsonify, send_from_directory, send_file
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from flask_jwt_extended import create_refresh_token, get_jwt_identity, jwt_required, get_jwt

from server.constants import institution_names, initial_categories
from server.controller.brand_controller import brand_controller
from server.controller.user_controller import user_controller
from server.models.brands import Category
from server.models.pre_registered_count import PreRegisteredCount, Institution
from server.models.user import User
from server import app, db
from server.services.user_services import generate_token

SWAGGER_URL = '/swagger'
API_URL = '/swagger.json'

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Studays API Server"
    }
)

CORS(app)

app.register_blueprint(user_controller)
app.register_blueprint(brand_controller)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file("uploads"+"\\"+filename)


@app.errorhandler(404)
def not_found(e):
    return f"This endpoint does not exist bro! {e}", 404


@app.errorhandler(401)
def custom_401(error):
    return jsonify({"message": "You are not authorized to access this page", "success": False}), 401


def generate_refresh_token(user_id, role):
    refresh_token = create_refresh_token(identity=user_id, additional_claims={"role": role})
    return refresh_token


@app.route('/token/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    claim = get_jwt()
    new_token = generate_refresh_token(current_user, claim["role"])
    return jsonify({"access_token": new_token, "success": True}), 200


@app.route('/install')
def install():
    try:
        count = PreRegisteredCount.query.get_or_404(1)
        return "Yeyyyy, You have already installed the server! Visit Swagger UI at http://localhost:5000/swagger"
    except:
        try:
            db.create_all()
            registered = PreRegisteredCount(registered=8001, limit=10000)
            db.session.add(registered)
            db.session.commit()
            new_user = User(first_name="Dr.", last_name="Admin",  email="admin@mystudays.com", password="studays", phone="911",
                            dob="2023-28-10",
                            institution_name="Nex Bangladesh", display_pic="", type="admin",
                            logged_with="Server", validation=True)
            db.session.add(new_user)
            for name in initial_categories:
                new_cat = Category(name=name, bg="")
                db.session.add(new_cat)

            for name in institution_names:
                new_institution = Institution(name=name)
                db.session.add(new_institution)

            # for dick in user_list:
            #     if "FUCK" not in dick["first_name"]:
            #         older_user = User(first_name=dick["first_name"], last_name=dick["last_name"], email=dick["email"],
            #                           password=dick["password"],
            #                           phone=dick["phone"],
            #                           dob=dick["dob"],
            #                           institution_name=dick["institution_name"],
            #                           display_pic="https://th.bing.com/th/id/R.f29406735baf0861647a78ae9c4bf5af?rik=GKTBhov2iZge9Q&riu="
            #                                       "http%3a%2f%2fcdn.onlinewebfonts.com%2fsvg%2fimg_206976.png&ehk=gCH45Zmryw3yqyqG%2fhd8W"
            #                                       "DQ53zwYfmC8K9OIkNHP%2fNU%3d&risl=&pid=ImgRaw&r=0", type=dick["type"],
            #                           logged_with="Email", validation=False)
            #         db.session.add(older_user)

            db.session.commit()
            return "Yeyyyy, You have successfully installed the server!"
        except Exception as e:
            return jsonify({"message": e})


@app.route('/status')
def status():
    return jsonify({"message": "Pre-Registration is Ongoing", "success": True, "is_pre_register": True})


@app.route('/status/dev')
def status_dev():
    return jsonify({"message": "Pre-Registration is Ongoing", "success": True, "is_pre_register": True})
    
    
@app.route('/status/dev1')
def status_dev_one():
    return jsonify({"message": "Pre-Registration is Ongoing", "success": True, "is_pre_register": False})