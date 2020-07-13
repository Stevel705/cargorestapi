# from flask_restful import Resource, Api, reqparse
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)

# Загрузим информацию о грузах и тарифе
with open(basedir + "/cargo.json", "r") as read_file:
    data_cargo = json.load(read_file)

# Получить rate по актуальной дате и типу груза


def get_rate(date, cargo_type):
    # Если такой даты нет, то вернуть False
    if data_cargo.get(date) is None:
        return False
    for el in data_cargo[date]:
        if el['cargo_type'] == cargo_type:
            return el['rate']

    # Если тип груза не найден
    return False


class Logging(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    cargoType = db.Column(db.String(200))
    declaredValue = db.Column(db.Float)
    rate = db.Column(db.Float)
    result = db.Column(db.Float)
    info = db.Column(db.String(10))

    def __init__(self, date, cargoType, declaredValue, rate, result, info):
        self.date = date
        self.cargoType = cargoType
        self.declaredValue = declaredValue
        self.rate = rate
        self.result = result
        self.info = info


@app.errorhandler(400)
def bad_request(e):
    # return also the code error
    return jsonify({"status": "not ok", "message": "this server could not understand your request"}), 400


@app.errorhandler(404)
def not_found(e):
    # return also the code error
    return jsonify({"status": "not found", "message": "route not found"}), 404


@app.route('/innoseti/api/v1.0/declared-value', methods=['GET'])
def declared_val():
    date_ = request.args.get('date')  # дата
    cargo_type = request.args.get('cargoType')  # тип груза
    declared_value = request.args.get('declaredValue')  # объявленная стоимость

    # Возвращаем информацию о недостаточной информации в запросе и записываем в бд
    if date_ is None or cargo_type is None or declared_value is None:
        new_log = Logging(None, cargo_type, declared_value, 0, 0, "Failed")
        db.session.add(new_log)
        db.session.commit()
        return "Not enough information about cargo. Need the date, type of cargo and declared value"

    # Получаем дату и приводим к первому дню месяца, используем эту дату для получения актуальной информации в json
    # Считаем, что дата приходит в нужном формате и нам не нужно её проверять
    rate = get_rate(date=date_, cargo_type=cargo_type)

    if not rate:
        return "No information about cargo"

    result = float(declared_value) * float(rate)

    new_log = Logging(datetime.strptime(date_, '%Y-%m-%d'),
                      cargo_type, declared_value, rate, result, "Success")
    db.session.add(new_log)
    db.session.commit()

    return jsonify({"result": result}), 200


@app.route('/', methods=["GET"])
def info_view():
    # List of routes for this API:
    output = {
        'info': 'GET /',
        'calculate declared value': 'GET /innoseti/api/v1.0/declared-value?date=yyyy-mm-dd&cargoType=cargo_type&declaredValue=declared_value',
    }
    return jsonify(output), 200


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
