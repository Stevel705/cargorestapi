from flask_restful import Resource, Api, reqparse
from flask import Flask, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__)) 

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
    date_ = request.args.get('date') # дата 
    cargo_type = request.args.get('cargoType') # тип груза 
    declared_value = request.args.get('declaredValue') # объявленная стоимость

    if date_ is None:
        return "No date"

    if cargo_type is None:
        return "No cargo type"
    
    if declared_value is None:
        return "No declared value"

    # Получаем дату и приводим к первому дню месяца, используем эту дату для получения актуальной информации в json
    # Считаем, что дата приходит в нужном формате и нам не нужно её проверять
    date_time = datetime.strptime(date_, '%Y-%m-%d').replace(day=1).strftime("%Y-%m-%d")
    rate = get_rate(date=date_time, cargo_type=cargo_type)
    
    if not rate:
        return "No information about cargo"

    result = float(declared_value) * float(rate)
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