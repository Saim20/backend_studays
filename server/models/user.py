from server import db
from server.models.auditable_mixin import AuditableMixin


class User(db.Model, AuditableMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    dob = db.Column(db.String(255), nullable=False)
    institution_name = db.Column(db.String, nullable=False)
    display_pic = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String, nullable=False)  # user / admin / manager
    logged_with = db.Column(db.String(255), default="Email")
    validation = db.Column(db.Boolean, default=False)
    education_level = db.Column(db.String(255), default="Undergraduate")
    subscription = db.relationship('Subscription', backref='user', uselist=False, lazy=True)
    payment_history = db.relationship('PaymentHistory', backref='user', lazy=True)

    def to_json(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "dob": self.dob,
            "institution_name": self.institution_name,
            'display_pic': self.display_pic.replace('server/', ''),
            "type": self.type,
            "subscription": self.subscription.to_json() if self.subscription else None,
            "payment_history": [payment.to_json() for payment in self.payment_history],
            "logged_with": self.logged_with,
            "validation": self.validation,
            "education_level": self.education_level,
        }


class PaymentHistory(db.Model, AuditableMixin):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    payment_type = db.Column(db.String(255), nullable=False)
    payment_reason = db.Column(db.String(255), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_json(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "payment_type": self.payment_type,
            "payment_reason": self.payment_reason,
            "paymentDate": self.created_at.isoformat()
        }


class Verification(db.Model, AuditableMixin):
    id = db.Column(db.Integer, primary_key=True)
    emailCode = db.Column(db.String(6), nullable=False)
    email_validation = db.Column(db.Boolean, default=False)
    id_validation = db.Column(db.Boolean, default=False)
    id_pic = db.Column(db.String(255), default='')
    user_id = db.Column(db.Integer, nullable=False)

    def to_json(self):
        return {
            'id': self.id,
            'emailCode': self.emailCode,
            'email_validation': self.email_validation,
            'id_validation': self.id_validation,
            'user_id': self.user_id,
            'id_pic': self.id_pic.replace('server/', '')
        }


class AvailableSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, unique=False, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def to_json(self):
        return {
            "id": self.id,
            "planName": self.plan_name,
            "description": self.description,
            "price": self.price,
        }


class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expiration_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    available_subscription_id = db.Column(db.Integer, nullable=False)

    def to_json(self):
        return {
            "id": self.id,
            "expirationDate": self.expiration_date.isoformat(),
            "user_id": self.user_id,
            "current_plan": self.available_subscription_id,
        }
