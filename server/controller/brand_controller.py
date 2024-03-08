from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask import Blueprint, request, jsonify

from server.models.brands import Brands
from server.services import brand_services

brand_controller = Blueprint('brand', __name__, url_prefix='/api/brand')


def check_admin_permission():
    claim = get_jwt()
    if claim['role'] == "user":
        return False, jsonify({'message': 'You are not Authorized!', "success": False}), 401
    return True


@brand_controller.route('/add', methods=['POST'])
@jwt_required()
def add_brand():
    access = check_admin_permission()
    if not access:
        return access[1]
    if 'logo' not in request.files or 'banner' not in request.files:
        return jsonify({'message': 'Logo or Banner Image Missing', "success": False})
    if 'name' not in request.form or 'description' not in request.form:
        return jsonify({'message': 'Parameters for adding Brand are missing', "success": False})

    name = request.form['name'],
    description = request.form['description'],
    logo_file = request.files['logo']
    banner_file = request.files['banner']
    return brand_services.add_brand(name, description, logo_file, banner_file)


@brand_controller.route('/all', methods=['GET'])
@jwt_required()
def get_brands():
    brands = Brands.query.all()
    brand_list = [brand.to_json() for brand in brands]
    return jsonify({'data': brand_list, "success": True})


@brand_controller.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_brand_by(id):
    brand = Brands.query.get_or_404(id)
    return jsonify({'data': brand.to_json(), "success": True})


@brand_controller.route('/coupon/add', methods=['POST'])
@jwt_required()
def add_coupon():
    # access = check_admin_permission()
    # if not access[0]:
    #     return access[1]
    if 'banner_main' not in request.files or 'banner_large' not in request.files:
        return jsonify({'message': 'Banner Images are Missing', "success": False})
    if 'limited' not in request.form or 'title' not in request.form or 'description' not in request.form or\
            'brand_id' not in request.form:
        return jsonify({'message': 'Parameters for adding Coupons are missing', "success": False})

    title = request.form['title']
    num_of_coupon = request.form['amount']
    description = request.form['description']
    category = request.form['category']
    saving = request.form['saving']
    limited = request.form['limited'] == "1"
    brand_id = int(request.form['brand_id'])
    banner_main = request.files['banner_main']
    banner_large = request.files['banner_large']

    return brand_services.add_coupons(title, description, limited, brand_id, banner_main, banner_large, num_of_coupon,
                                      category, saving)


@brand_controller.route('/coupon/all', methods=['GET'])
@jwt_required()
def get_all_coupon():
    return brand_services.get_all_coupon()


@brand_controller.route('/coupon/unlock/<int:id>', methods=['GET'])
@jwt_required()
def unlock_coupon(id):
    current_user = get_jwt_identity()
    return brand_services.unlock_coupon(current_user, id)


@brand_controller.route('/coupon/saved', methods=['GET'])
@jwt_required()
def get_saved():
    current_user = get_jwt_identity()
    return brand_services.get_saved(current_user)


@brand_controller.route('/coupon/saved/remove/<int:id>', methods=['DELETE'])
@jwt_required()
def remove_saved(id):
    current_user = get_jwt_identity()
    return brand_services.remove_saved(current_user, id)


@brand_controller.route('/coupon/save/<int:id>', methods=['POST'])
@jwt_required()
def save_coupon_of_user(id):
    current_user = get_jwt_identity()
    id = int(id)
    return brand_services.save_coupon(id, current_user)


@brand_controller.route('/coupon/search', methods=['GET'])
@jwt_required()
def search_coupon():
    search_query = request.args.get('search_term')
    category = request.args.get('category')
    return brand_services.search_coupon(search_query, category)


@brand_controller.route('/offers/add', methods=['POST'])
@jwt_required()
def add_offer():
    # access = check_admin_permission()
    # if not access[0]:
    #     return access[1]
    if 'banner' not in request.files:
        return jsonify({'message': 'Banner Image is Missing', "success": False})
    banner = request.files['banner']
    return brand_services.add_offer(banner)


@brand_controller.route('coupon/saved/all', methods=['GET'])
@jwt_required()
def get_all_saved():
    current_user = get_jwt_identity()
    return brand_services.get_all_saved(current_user)

@brand_controller.route('/offers/', methods=['GET'])
@jwt_required()
def get_all_offers():
    return brand_services.get_all_offers()


@brand_controller.route('/categorys/add', methods=['POST'])
@jwt_required()
def add_category():
    # access = check_admin_permission()
    # if not access[0]:
    #     return access[1]
    data = request.get_json()
    return brand_services.add_category(data)


@brand_controller.route('/categorys/', methods=['GET'])
@jwt_required()
def get_all_category():
    return brand_services.get_all_category()


