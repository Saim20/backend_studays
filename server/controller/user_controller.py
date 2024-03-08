from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask import Blueprint, request, jsonify
from server.services import user_services

user_controller = Blueprint('user', __name__, url_prefix='/api/user')


def check_admin_permission():
    claim = get_jwt()
    if claim['role'] == "user":
        return False, jsonify({'message': 'You are not Authorized!', "success": False}), 401
    return True


@user_controller.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    return user_services.login(data)


@user_controller.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    access = check_admin_permission()
    if not access:
        return access[1]
    return user_services.delete_user(id)


@user_controller.route('/', methods=['DELETE'])
@jwt_required()
def delete_own():
    current_user = get_jwt_identity()
    return user_services.delete_user(current_user)


@user_controller.route('/add/admin', methods=['POST'])
@jwt_required()
def add_admin():
    access = check_admin_permission()
    if not access:
        return access[1]
    data = request.get_json()
    return user_services.insert_user(data, "admin")


@user_controller.route('/add/manager', methods=['POST'])
@jwt_required()
def add_manager():
    access = check_admin_permission()
    if not access:
        return access[1]
    data = request.get_json()
    return user_services.insert_user(data, "manager")


@user_controller.route('/register', methods=['POST'])
def add_user():
    data = request.get_json()
    return user_services.insert_user(data, "user")


@user_controller.route('/connect/google', methods=['POST'])
def connect_with_google():
    data = request.get_json()
    return user_services.connect_via_google(data)


@user_controller.route('/', methods=['PUT'])
@jwt_required()
def update_current_user():
    current_user = get_jwt_identity()
    data = request.get_json()
    return user_services.update_user(current_user, data)


@user_controller.route('/upload/profilepic', methods=['PUT'])
@jwt_required()
def update_profile_pic():
    current_user = get_jwt_identity()
    image = request.files['file']
    return user_services.update_profile_pic(current_user, image)


@user_controller.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id: int):
    data = request.get_json()
    return user_services.update_user(id, data)


@user_controller.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    current_user = get_jwt_identity()
    data = request.get_json()
    return user_services.change_password(current_user, data)


@user_controller.route('/', methods=['GET'])
@jwt_required()
def get_user():
    current_user = get_jwt_identity()
    return user_services.get_user(current_user)


@user_controller.route('/verify/email/<code>', methods=['GET'])
@jwt_required()
def verify_email(code):
    current_user = get_jwt_identity()
    return user_services.verify_email(current_user, code)


@user_controller.route('/verify/status', methods=['GET'])
@jwt_required()
def get_verification_status():
    current_user = get_jwt_identity()
    return user_services.get_verification_info(current_user)


@user_controller.route('/verification', methods=['POST'])
@jwt_required()
def submit_verification():
    current_user = get_jwt_identity()
    image = request.files['file']
    return user_services.verify_id(current_user, image)


@user_controller.route('/verification/approve/<int:id>', methods=['POST'])
@jwt_required()
def approve_id_verification(id: int):
    return user_services.approve_id(id)
    
    
@user_controller.route('/verification/approve/ff/<int:id>', methods=['POST'])
@jwt_required()
def approve_id_verification_ff(id: int):
    return user_services.approve_id_ff(id)
    

@user_controller.route('/add/subs/<int:id>', methods=['GET'])
@jwt_required()
def add_subs(id: int):
    return user_services.add_empty_subscription(id)


@user_controller.route('/verification/reject/<int:id>', methods=['POST'])
@jwt_required()
def reject_id_verification(id: int):
    return user_services.reject_id(id)


@user_controller.route('/payments/<int:user>', methods=['GET'])
@jwt_required()
def get_user_payments(user: int):
    return user_services.get_user_payment(user)


@user_controller.route('/payments/', methods=['GET'])
@jwt_required()
def get_own_payments():
    current_user = get_jwt_identity()
    return user_services.get_user_payment(current_user)


@user_controller.route('/all/<string:type>', methods=['GET'])
@jwt_required()
def get_all_user_by(type):
    access = check_admin_permission()
    if not access:
        return access[1]
    return user_services.get_all_user_by(type)


@user_controller.route('/institutions', methods=['GET'])
def get_institutions():
    return user_services.get_institutions()


@user_controller.route('/institutions/add', methods=['POST'])
@jwt_required()
def add_institution():
    access = check_admin_permission()
    if not access:
        return access[1]
    data = request.get_json()
    return user_services.add_institutions(data)


@user_controller.route('/institutions/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_institution(id):
    access = check_admin_permission()
    if not access:
        return access[1]
    return user_services.delete_institution(id)


@user_controller.route('/all', methods=['GET'])
@jwt_required()
def get_all_user():
    return user_services.get_all_user()


@user_controller.route('/waiting', methods=['GET'])
def get_wait_list():
    return user_services.get_waiting()



