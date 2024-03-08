from server import db


class PreRegisteredCount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registered = db.Column(db.Integer, nullable=False)
    limit = db.Column(db.Integer, nullable=False)

    def to_json(self):
        return {"id": self.id, "registered": self.registered, "limit": self.limit}


class Institution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer, nullable=False)

    def to_json(self):
        return {"id": self.id, "name": self.name}
