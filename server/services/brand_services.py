import os
import random
import string

from flask import jsonify
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from server import app, db
from server.constants import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from server.models.brands import Brands, Coupon, Offers, Category, CouponCode, Saved
from server.models.user import PaymentHistory
from server.services.user_services import validate_request_body

app.config['UPLOADED_PHOTOS_DEST'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def add_brand(name, description, logo_file, banner_file):
    if not (logo_file and allowed_file(logo_file.filename)) or not (banner_file and allowed_file(banner_file.filename)):
        return jsonify({'message': 'Error: Invalid file extension', "success": False})
    logo_filename = secure_filename(logo_file.filename)
    banner_filename = secure_filename(banner_file.filename)

    logo_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], logo_filename)
    banner_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], banner_filename)

    print(logo_path)

    logo_file.save(logo_path)
    banner_file.save(banner_path)
    new_brand = Brands(
        name=name[0],
        logo=logo_path.replace('\\', '/'),
        banner=banner_path.replace('\\', '/'),
        description=description[0]
    )

    db.session.add(new_brand)
    db.session.commit()

    return jsonify({'message': 'Brand has been added successfully', "success": True})


def add_coupons(title, description, limited, brand_id, banner_main, banner_large, num_of_coupon, category, saving):
    if not (banner_main and allowed_file(banner_main.filename)) or not (
            banner_large and allowed_file(banner_large.filename)):
        return jsonify({'message': 'Error: Invalid file extension', "success": False})
    banner_main_filename = secure_filename(banner_main.filename)
    banner_large_filename = secure_filename(banner_large.filename)

    banner_main_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], banner_main_filename)
    banner_large_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], banner_large_filename)

    banner_main.save(banner_main_path)
    banner_large.save(banner_large_path)

    new_coupon = Coupon(
        title=title,
        description=description,
        banner_main=banner_main_path.replace('\\', '/'),
        banner_large=banner_large_path.replace('\\', '/'),
        limited=limited,
        brand_id=brand_id,
        category=category,
        saving=saving
    )

    db.session.add(new_coupon)
    db.session.commit()

    for i in range(int(num_of_coupon)):
        unique_code = generate_coupon_code()

        while CouponCode.query.filter_by(code=unique_code).first() is not None:
            unique_code = generate_coupon_code()

        new_coupon_code = CouponCode(
            code=unique_code,
            coupon_id=new_coupon.id,
        )

        db.session.add(new_coupon_code)

    db.session.commit()
    return jsonify({'message': 'Coupon has been added successfully', "success": True})


def generate_coupon_code(length=6):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def add_offer(banner):
    if not (banner and allowed_file(banner.filename)):
        return jsonify({'message': 'Error: Invalid file extension', "success": False})

    banner_filename = secure_filename(banner.filename)
    banner_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], banner_filename)
    banner.save(banner_path)

    new_offer = Offers(banner=banner_path.replace('\\', '/'))
    db.session.add(new_offer)
    db.session.commit()

    return jsonify({'message': 'Offer has been added successfully', "success": True})


def get_all_offers():
    offers = Offers.query.all()
    offers_list = [offer.to_json() for offer in offers]
    return jsonify({'data': offers_list, "success": True})


def add_category(data):
    validate = validate_request_body(data, ["name"])
    if not validate[0]:
        return jsonify({"message": validate[1], "success": False}), 400
    new_cat = Category(name=data['name'])

    db.session.add(new_cat)
    db.session.commit()

    return jsonify({'message': 'Category has been added successfully', "success": True})


def get_all_category():
    cats = Category.query.all()
    cat_list = [cat.to_json() for cat in cats]
    return jsonify({'data': cat_list, "success": True})


def get_all_coupon():
    coupons = Coupon.query.all()
    coupon_list = [coupon.to_json() for coupon in coupons]
    return jsonify({'data': coupon_list, "success": True})


def unlock_coupon(current_user, coupon_id):
    coupon_code = CouponCode.query.filter_by(coupon_id=coupon_id, used=False).first()
    json_data = coupon_code.to_json()
    coupon_code.used = True
    coupon = Coupon.query.get_or_404(coupon_id)
    payment = PaymentHistory(amount = 0, payment_type = "Coupon", payment_reason=coupon.title, user_id=current_user)
    db.session.add(payment)
    db.session.add(coupon_code)
    db.session.commit()
    return jsonify({'data': json_data, "success": True})


def get_saved(current_user):
    try:
        coupon_list = []
        saved = Saved.query.filter_by(user_id=current_user).first()
        if saved:
            coupons = Coupon.query.filter(Coupon.id.in_(saved.coupon_ids)).all()
            coupon_list = [coupon.to_json() for coupon in coupons]
        return jsonify({'data': coupon_list, "success": True})
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


def search_coupon(search_query, category):
    if not search_query:
        return jsonify({'message': 'Please provide a search query', "success": True}), 400
    base_query = Coupon.query.filter(
        or_(
            Coupon.title.ilike(f"%{search_query}%"),
            Coupon.brand.has(Brands.name.ilike(f"%{search_query}%"))
        )
    )
    if category:
        base_query = base_query.filter(Coupon.category.ilike(f"%{category}%"))

    coupons = base_query.all()
    search_results = [coupon.to_json() for coupon in coupons]

    return jsonify({'data': search_results, "success": True})


def remove_saved(current_user, id):
    saved = Saved.query.filter_by(user_id=current_user).first()
    if saved:
        saved.remove_coupon_id(id)
    else:
        saved = Saved(current_user, [])

    db.session.add(saved)
    db.session.commit()

    return jsonify({'message': 'Coupon has been removed successfully', "success": True})


def save_coupon(id, current_user):
    saved = Saved.query.filter_by(user_id=current_user).first()
    if saved:
        saved.add_coupon_id(id)
    else:
        saved = Saved(current_user, [1])

    db.session.add(saved)
    db.session.commit()
    return jsonify({'message': 'Coupon has been saved successfully', "success": True})


def get_all_saved(current_user):
    saved = Saved.query.filter_by(user_id=current_user).first()
    if not saved:
        saved = Saved(current_user, [])
        db.session.add(saved)
        db.session.commit()

    return jsonify({'data': saved.coupon_ids, "success": True})