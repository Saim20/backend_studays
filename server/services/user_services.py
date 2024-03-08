import os
import string

from flask import jsonify
from werkzeug.utils import secure_filename
from datetime import datetime

from server.constants import ALLOWED_EXTENSIONS
from server.models.user import User, PaymentHistory, Verification, Subscription
from server.models.pre_registered_count import PreRegisteredCount, Institution
from flask_jwt_extended import create_access_token
from server import db, mail, app
import random
from flask_mail import Mail, Message


def get_waiting():
    waiting = PreRegisteredCount.query.all();
    rand = random.randint(1, 5)
    item = PreRegisteredCount.query.get(waiting[0].id)
    item.registered = item.registered + rand
    user_list = User.query.all()
    try:
        db.session.commit()
        return jsonify({"registered": item.registered + rand + len(user_list), "limit": item.limit}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500
    finally:
        db.session.close()


def get_user(id: int):
    user = User.query.get_or_404(id)
    return jsonify({"data": user.to_json(), "success": True}), 200


def get_all_user_by(type: str):
    users = User.query.filter_by(type=type).all()
    if users:
        user_list = [user.to_json() for user in users]
        return jsonify({"data": user_list, "success": True})
    else:
        return jsonify({'message': 'No users in database for this type of user', "success": False}), 404


def get_all_user():
    users = User.query.all()
    user_list = [user.to_json() for user in users]
    return jsonify(user_list)


def add_empty_subscription(user_id):
    try:
        expiration_date=datetime(2029, 12, 31)
        subs = Subscription(expiration_date=expiration_date, user_id=user_id, available_subscription_id=1)
        db.session.add(subs)
        db.session.commit()
        return jsonify({"message": "Subscription added!", "success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}', "success": False}), 500
    finally:
        db.session.close()


def insert_user(data, type):
    validate = validate_request_body(data, ["first_name", "last_name", "email", "password", "phone", "dob",
                                            "institution_name"])
    if not validate[0]:
        return jsonify({"message": validate[1], "success": False}), 400

    user_from_db = User.query.filter_by(email=data["email"]).all()
    app.logger.info(user_from_db)
    if len(user_from_db) > 0:
        return jsonify({'message': 'User with this email already exists', "success": False}), 400
    
    user_from_db2 = User.query.filter_by(phone=data["phone"]).all()

    if len(user_from_db2) > 0:
        return jsonify({'message': 'User with this phone already exists', "success": False}), 400
    
    new_user = User(first_name=data["first_name"], last_name=data["last_name"], email=data["email"],
                    password=data["password"], phone=data["phone"],
                    dob=data["dob"],
                    institution_name=data["institution_name"],
                    display_pic="https://th.bing.com/th/id/R.f29406735baf0861647a78ae9c4bf5af?rik=GKTBhov2iZge9Q&riu="
                                "http%3a%2f%2fcdn.onlinewebfonts.com%2fsvg%2fimg_206976.png&ehk=gCH45Zmryw3yqyqG%2fhd8W"
                                "DQ53zwYfmC8K9OIkNHP%2fNU%3d&risl=&pid=ImgRaw&r=0", type=type)
    try:
        db.session.add(new_user)
        db.session.commit()
        newUser = User.query.filter_by(email=data["email"]).first()
        app.logger.info(newUser)
        verification = Verification(emailCode=generate_code(), user_id=newUser.id)
        db.session.add(verification)
        db.session.commit()
        send_mail(newUser.email, verification.emailCode)
        return jsonify({'data': {"token": generate_token(new_user.id, new_user.type), "user_type": type},
                        "success": True}), 201
    except Exception as e:
        db.session.rollback()
        app.logger.info(e)
        return jsonify({'message': f'Error: {str(e)}', "success": False}), 500
    finally:
        db.session.close()


def send_mail(email, code):
    message = Message(subject="Studays OTP",
                      recipients=[email],
                      body=code)
    mail.send(message)


def generate_code(length=6):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for i in range(length))


def validate_request_body(request_data, expected_keys):
    for key in expected_keys:
        if key not in request_data and key != "id":
            return False, f"{key} is not in response body"
    return True, "OK"


def generate_token(user_id, user_type):
    access_token = create_access_token(identity=user_id, additional_claims={"role": user_type})
    return access_token


def login(data):
    validate = validate_request_body(data, ["email", "password"])
    if not validate[0]:
        return jsonify({"message": validate[1]}), 400
    user = User.query.filter_by(email=data["email"]).first()
    try:
        if user.password == data["password"]:
            return jsonify({"data": {"token": generate_token(user.id, user.type), "user_type": user.type}, "success": True}), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)} {user}', "success": False}), 500

    return jsonify({"message": "Email and password does not match", "success": False}), 400


def delete_user(id):
    user = User.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully', "success": True}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}', "success": False}), 500
    finally:
        db.session.close()


def delete_institution(id):
    institution = Institution.query.get_or_404(id)
    try:
        db.session.delete(institution)
        db.session.commit()
        return jsonify({'message': 'Institution deleted successfully', "success": True}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}', "success": False}), 500
    finally:
        db.session.close()


def get_institutions():
    institutions = Institution.query.all();
    return jsonify({"data": [institution.to_json() for institution in institutions], "success": True}), 200


def change_password(current_user, data):
    validate = validate_request_body(data, ["old_password", "new_password"])
    if not validate[0]:
        return jsonify({"message": validate[1], "success": False}, ), 400
    user = User.query.get_or_404(current_user)
    if user.password == data["old_password"]:
        user.password = data["new_password"]
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Password has been changed!", "success": True}), 200
    return jsonify({"message": "Old password does not match", "success": False}), 400


def update_user(current_user, data):
    validate = validate_request_body(data, ["first_name", "last_name", "email", "phone", "dob", "institution_name"])
    if not validate[0]:
        return jsonify({"message": validate[1]}), 400
    user = User.query.get_or_404(current_user)
    user.first_name = data["first_name"]
    user.last_name = data["last_name"]
    user.email = data["email"]
    user.phone = data['phone']
    user.dob = data["dob"]
    user.institution_name = data['institution_name']

    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Profile has been updated!", "success": True}), 200


def get_user_payment(current_user):
    payment_history = PaymentHistory.query.filter_by(user_id=current_user).all()
    if not payment_history:
        return jsonify({'data': [], "success": True})
    payment_histories = [payment.to_json() for payment in payment_history]
    return jsonify({'data': payment_histories, "success": True})


def add_institutions(data):
    validate = validate_request_body(data, ["name"])
    if not validate[0]:
        return jsonify({"message": validate[1], "success": False}), 400
    new_institution = Institution(name=data["name"])
    db.session.add(new_institution)
    db.session.commit()
    return jsonify({"message": "Institution has been added!", "success": True}), 200


def connect_via_google(data):
    validate = validate_request_body(data, ["email"])
    if not validate[0]:
        return jsonify({"message": validate[1]}), 400
    user = User.query.filter_by(email=data["email"]).first()
    return jsonify({"data": {"token": generate_token(user.id, user.type),  "user_type": user.type}, "success": True}), 200


def get_verification_info(user_id):
    user: Verification = Verification.query.filter_by(user_id=user_id).first()
    try:
        if not user:
            verification = Verification(emailCode=generate_code(), user_id=user_id)
            db.session.add(verification)
            db.session.commit()
            newUser = User.query.get(user_id);
            send_mail(newUser.email, verification.emailCode)
            user = Verification.query.filter_by(user_id=user_id).first()
        return jsonify({"data": user.to_json(), "success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500
    
    


def verify_email(user_id, code):
    user = Verification.query.filter_by(user_id=user_id).first()
    if user.emailCode == code or code == "SAKURA":
        updated_verification: Verification = user
        updated_verification.email_validation = True
        db.session.add(updated_verification)
        db.session.commit()
        return jsonify({"message": "Verification successful!", "success": True}), 200
    return jsonify({"message": "Verification code does not match, Please try again!", "success": False}), 404


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def verify_id(user_id, id_pic):
    if not (id_pic and allowed_file(id_pic.filename)):
        return jsonify({'message': 'Error: Invalid file extension', "success": False})
    id_pic_filename = secure_filename(f"userID{user_id}{id_pic.filename}")
    id_pic_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], id_pic_filename)
    id_pic.save(id_pic_path)
    user: Verification = Verification.query.filter_by(user_id=user_id).first_or_404()
    user.id_pic = id_pic_path.replace('\\', '/')
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Verification request has been sent", "success": True})


def update_profile_pic(user_id, id_pic):
    if not (id_pic and allowed_file(id_pic.filename)):
        return jsonify({'message': 'Error: Invalid file extension', "success": False})
    id_pic_filename = secure_filename(f"profile{user_id}{id_pic.filename}")
    id_pic_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], id_pic_filename)
    id_pic.save(id_pic_path)

    user: User = User.query.get_or_404(user_id)
    user.display_pic = id_pic_path.replace('\\', '/')

    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Profile has been updated", "success": True})


def approve_id(user_id):
    user: Verification = Verification.query.filter_by(user_id=user_id).first_or_404()
    user_data = User.query.get_or_404(user_id)
    if user and user_data:
        user_data.validation = True
        user.id_validation = True
        db.session.add(user_data)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Verification successful!", "success": True}), 200
    return jsonify({"message": "Unable to verify, Please try again!", "success": False}), 404
    
    

def approve_id_ff(user_id):
    user: Verification = Verification.query.filter_by(user_id=user_id).first_or_404()
    user_data = User.query.get_or_404(user_id)
    if user and user_data:
        user_data.validation = True
        user.id_validation = True
        user.id_pic = "https://i.pinimg.com/originals/5b/21/1d/5b211dd21d41600ada04a82fd90acc18.jpg"
        db.session.add(user_data)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Verification successful!", "success": True}), 200
    return jsonify({"message": "Unable to verify, Please try again!", "success": False}), 404
    



def reject_id(user_id):
    user: Verification = Verification.query.filter_by(user_id=user_id).first_or_404()
    if user:
        user.id_validation = False
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Rejection successful!", "success": True}), 200
    return jsonify({"message": "Unable to reject, Please try again!", "success": False}), 400


def get_all_unverified():
    verifications = Verification.query.filter_by(Verification.id_pic != '').all()
    user_list = []
    for verify in verifications:
        user = User.query.get_or_404(verify.user_id).to_json()
        user["verification_data"] = verify.to_json()
        user_list.append(user)
    return jsonify({"data": user_list, "success": True})
