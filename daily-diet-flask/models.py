from datetime import datetime

from database import db


class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False, default="")
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    is_on_diet = db.Column(db.Boolean, nullable=False, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "date_time": self.date_time.isoformat(),
            "is_on_diet": self.is_on_diet,
        }
