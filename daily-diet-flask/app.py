from datetime import datetime

from flask import Flask, jsonify, request

from database import db
from models import Meal


def create_app(database_uri="sqlite:///daily_diet.db"):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["JSON_SORT_KEYS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    def parse_date_time(value):
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            return None

    def validate(data, partial=False):
        """Retorna (dados_limpos, erro)."""
        if not isinstance(data, dict):
            return None, "Corpo da requisição inválido"

        clean = {}

        if "name" in data or not partial:
            name = data.get("name")
            if not isinstance(name, str) or not name.strip():
                return None, "O campo 'name' é obrigatório"
            clean["name"] = name.strip()

        if "description" in data or not partial:
            description = data.get("description")
            if not isinstance(description, str):
                return None, "O campo 'description' é obrigatório"
            clean["description"] = description

        if "date_time" in data or not partial:
            date_time = parse_date_time(data.get("date_time"))
            if date_time is None:
                return None, "O campo 'date_time' é obrigatório (ex.: 2026-11-04T12:30:00)"
            clean["date_time"] = date_time

        if "is_on_diet" in data or not partial:
            is_on_diet = data.get("is_on_diet")
            if not isinstance(is_on_diet, bool):
                return None, "O campo 'is_on_diet' é obrigatório (true ou false)"
            clean["is_on_diet"] = is_on_diet

        return clean, None

    @app.route("/meals", methods=["POST"])
    def create_meal():
        clean, error = validate(request.get_json(silent=True))
        if error:
            return jsonify({"message": error}), 400

        meal = Meal(**clean)
        db.session.add(meal)
        db.session.commit()
        return jsonify({"message": "Refeição cadastrada com sucesso", "meal": meal.to_dict()}), 201

    @app.route("/meals", methods=["GET"])
    def list_meals():
        meals = Meal.query.order_by(Meal.date_time.desc()).all()
        return jsonify([meal.to_dict() for meal in meals]), 200

    @app.route("/meals/<int:meal_id>", methods=["GET"])
    def get_meal(meal_id):
        meal = db.session.get(Meal, meal_id)
        if meal is None:
            return jsonify({"message": "Refeição não encontrada"}), 404
        return jsonify(meal.to_dict()), 200

    @app.route("/meals/<int:meal_id>", methods=["PUT"])
    def update_meal(meal_id):
        meal = db.session.get(Meal, meal_id)
        if meal is None:
            return jsonify({"message": "Refeição não encontrada"}), 404

        clean, error = validate(request.get_json(silent=True), partial=True)
        if error:
            return jsonify({"message": error}), 400

        for field, value in clean.items():
            setattr(meal, field, value)
        db.session.commit()
        return jsonify({"message": "Refeição atualizada com sucesso", "meal": meal.to_dict()}), 200

    @app.route("/meals/<int:meal_id>", methods=["DELETE"])
    def delete_meal(meal_id):
        meal = db.session.get(Meal, meal_id)
        if meal is None:
            return jsonify({"message": "Refeição não encontrada"}), 404

        db.session.delete(meal)
        db.session.commit()
        return jsonify({"message": "Refeição removida com sucesso"}), 200

    @app.route("/meals/metrics", methods=["GET"])
    def metrics():
        meals = Meal.query.order_by(Meal.date_time.asc()).all()
        on_diet = sum(1 for m in meals if m.is_on_diet)

        best_sequence = current = 0
        for meal in meals:
            current = current + 1 if meal.is_on_diet else 0
            best_sequence = max(best_sequence, current)

        return jsonify({
            "total_meals": len(meals),
            "meals_on_diet": on_diet,
            "meals_off_diet": len(meals) - on_diet,
            "best_sequence_on_diet": best_sequence,
        }), 200

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
