from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from data_manager import data_manager
from expense_predictor import predict_payer, get_next_payer

app = Flask(__name__, static_folder='../build', static_url_path='/')
CORS(app)

@app.route('/api/add_expense', methods=['POST'])
def add_expense():
    data = data_manager.load_data()
    expense_data = request.json
    expense_type = expense_data.get('category', '').strip().lower()
    amount = expense_data.get('amount')
    payer = expense_data.get('payer', '').strip().lower()
    rejected_payers = [p.lower() for p in expense_data.get('rejected_payers', [])]

    if not expense_type or amount is None:
        return jsonify({'error': 'Category and amount are required'}), 400

    if not payer:
        suggested_payer, reason = predict_payer(expense_type, amount, data)

        if suggested_payer is None:
            return jsonify({
                'message': reason,
                'confirmed': False
            }), 200

        if suggested_payer.lower() not in rejected_payers:
            expense = {"type": expense_type, "amount": amount, "payer": suggested_payer, "confirmed": False}
            data.append(expense)
            data_manager.save_data(data)
            return jsonify({
                'payer': suggested_payer,
                'confirmed': False,
                'message': f"A new bill for {expense_type} costing ${amount} just came in. {suggested_payer}, would you like to pay this bill?",
                'reason': reason
            })
        else:
            return jsonify({
                'message': 'All potential payers have rejected. Consider splitting the bill.',
                'confirmed': False
            }), 200

    expense = {"type": expense_type, "amount": amount, "payer": payer, "confirmed": True}
    data.append(expense)
    data_manager.save_data(data)
    thank_you_message = f"Thank you {payer}, for agreeing to pay the {expense_type} bill of ${amount}. We appreciate it!"
    return jsonify({'payer': payer, 'confirmed': True, 'message': thank_you_message})

@app.route('/api/reject_payment', methods=['POST'])
def reject_payment():
    data = data_manager.load_data()
    rejection_data = request.json
    rejected_payer = rejection_data.get('payer', '').lower()
    expense_type = rejection_data.get('category', '').strip().lower()
    amount = rejection_data.get('amount')
    rejected_payers = rejection_data.get('rejected_payers', [])

    if not data:
        return jsonify({'error': 'No expenses found'}), 400

    # Remove the last unconfirmed expense
    if not data[-1]['confirmed']:
        data.pop()

    # Find the next suggested payer
    suggested_payer, reason = get_next_payer(expense_type, amount, data, rejected_payers)

    if suggested_payer is None:
        return jsonify({
            'message': reason,
            'confirmed': False
        }), 200

    expense = {"type": expense_type, "amount": amount, "payer": suggested_payer, "confirmed": False}
    data.append(expense)
    data_manager.save_data(data)

    return jsonify({
        'payer': suggested_payer,
        'confirmed': False,
        'message': f"A new bill for {expense_type} costing ${amount} just came in. {suggested_payer}, would you like to pay this bill?",
        'reason': reason
    })

@app.route('/api/confirm_payment', methods=['POST'])
def confirm_payment():
    data = data_manager.load_data()
    payment_data = request.json
    payer = payment_data.get('payer', '').lower()

    if data and not data[-1]['confirmed']:
        data[-1]['payer'] = payer
        data[-1]['confirmed'] = True
        data_manager.save_data(data)
        expense_type = data[-1]['type']
        amount = data[-1]['amount']
        thank_you_message = f"Thank you {payer}, for agreeing to pay the {expense_type} bill of ${amount}. We appreciate it!"
        return jsonify({'message': thank_you_message})
    else:
        return jsonify({'error': 'No pending expense found'}), 400

@app.route('/api/analyze_expenses', methods=['GET'])
def analyze_expenses():
    data = data_manager.load_data()
    analysis_result = {}

    for expense in data:
        if expense['confirmed']:
            category = expense['type'].lower()
            payer = expense['payer'].lower()
            amount = float(expense['amount'])

            if category not in analysis_result:
                analysis_result[category] = {}
            if payer not in analysis_result[category]:
                analysis_result[category][payer] = 0
            analysis_result[category][payer] += amount

    formatted_result = []
    for category, payers in analysis_result.items():
        category_result = f"Category: {category.capitalize()}\n"
        sorted_payers = sorted(payers.items(), key=lambda x: x[1], reverse=True)
        for i, (payer, amount) in enumerate(sorted_payers, 1):
            category_result += f"{i}. {payer.capitalize()}: ${amount:.2f}\n"
        formatted_result.append(category_result)

    final_result = '\n\n'.join(formatted_result)
    return jsonify({'analysis': final_result})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)