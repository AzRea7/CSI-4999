from flask import Blueprint, request, jsonify

mortgage_api = Blueprint('mortgage_api', __name__)

@mortgage_api.route('/api/mortgage', methods=['GET'])
def mortgage():
    price = float(request.args.get('price', 0))
    down_payment = float(request.args.get('down_payment', 0))
    interest_rate = float(request.args.get('interest_rate', 6)) / 100
    years = int(request.args.get('years', 30))

    loan_amount = price - down_payment
    n = years * 12
    r = interest_rate / 12

    monthly_payment = loan_amount * r * (1 + r)**n / ((1 + r)**n - 1)
    return jsonify({"monthly_payment": round(monthly_payment, 2)})
