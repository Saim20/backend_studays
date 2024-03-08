import json

from server import db
from server.models.auditable_mixin import AuditableMixin


class Coupon(db.Model, AuditableMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=False, nullable=False)
    description = db.Column(db.Text, unique=False, nullable=False)
    banner_main = db.Column(db.String(255), unique=False, nullable=False)
    banner_large = db.Column(db.String(255), unique=False, nullable=False)
    limited = db.Column(db.Boolean, default=True)
    category = db.Column(db.String(255), unique=False, nullable=False)
    saving = db.Column(db.String(255), unique=False, nullable=False)
    coupon_codes = db.relationship('CouponCode', backref='coupon', lazy=True)

    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)

    def to_json(self):
        used_num = len([coupon_code for coupon_code in self.coupon_codes if not coupon_code.used])
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'saving': self.saving,
            'limited': self.limited,
            'banner_main': self.banner_main.replace('server/', ''),
            'banner_large': self.banner_large.replace('server/', ''),
            'brand_id': self.brand_id,
            'coupons_left': f'{used_num} Left' if self.limited else 'Unlimited',
            'coupon_codes': [coupon_code.to_json() for coupon_code in self.coupon_codes]
        }


class CouponCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(12), unique=True, nullable=False)
    used = db.Column(db.Boolean, default=False)

    coupon_id = db.Column(db.Integer, db.ForeignKey('coupon.id'), nullable=False)

    def to_json(self):
        return {
            'id': self.id,
            'code': self.code,
            'coupon_id': self.coupon_id,
            'used': self.used,
        }


class Saved(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    coupon_ids_json = db.Column(db.String, nullable=True)

    def __init__(self, user_id, coupon_ids=None):
        self.user_id = user_id
        self.coupon_ids = coupon_ids

    @property
    def coupon_ids(self):
        return json.loads(self.coupon_ids_json) if self.coupon_ids_json else []

    @coupon_ids.setter
    def coupon_ids(self, value):
        self.coupon_ids_json = json.dumps(value) if value else None

    def add_coupon_id(self, coupon_id):
        current_ids = self.coupon_ids
        current_ids.append(coupon_id)
        self.coupon_ids = current_ids

    def remove_coupon_id(self, coupon_id):
        current_ids = self.coupon_ids
        if coupon_id in current_ids:
            current_ids.remove(coupon_id)
            self.coupon_ids = current_ids


class Offers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    banner = db.Column(db.String(255), unique=True, nullable=False)

    def to_json(self):
        return {
            'id': self.id,
            'banner': self.banner.replace('server/', ''),
        }


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bg = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), unique=True, nullable=False)

    def to_json(self):
        return {
            'id': self.id,
            'bg': self.bg.replace('server/', ''),
            'name': self.name,
        }


class Brands(db.Model, AuditableMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    logo = db.Column(db.String(255), unique=True, nullable=False)
    banner = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text, unique=True, nullable=False)

    coupons = db.relationship('Coupon', backref='brand', lazy=True)

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'logo': self.logo.replace('server/', ''),
            'banner': self.banner.replace('server/', ''),
            'coupons': [coupon.to_json() for coupon in self.coupons],
        }
