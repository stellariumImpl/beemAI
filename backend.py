from flask import Flask, request, jsonify, send_from_directory
import openai
import os
import json

app = Flask(__name__)

# Set OpenAI API key
openai.api_key = 'sk-proj-qKyvdZ65iHWGtfM3lqAJT3BlbkFJ1fU7402aW4gSLXk8nnEB'

def load_data(filepath):
    """Load JSON data from a file"""
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_data(filepath, data):
    """Save JSON data to a file"""
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)

def predict_payer(expense_type, amount, data):
    """Predict the payer using OpenAI based on historical data"""
    # Filter data to include only entries of the same type as the current expense
    filtered_data = [item for item in data if item['type'] == expense_type]
    # Take the last 6 payments of the same type, if there are fewer, take as many as are available
    historical_data = ' '.join([f"{item['type']} ${item['amount']} payed by {item['payer']}" for item in filtered_data[-6:]])
    print(historical_data)
    if not historical_data:
        return data[-1]['payer']
    prompt = f"Here are previous expense payments {historical_data}. Given a new expense for {expense_type} costing ${amount}, who is the most possible person that will pay? Your answer must be a single in the format: 'Name'. "
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are an assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    print(response)
    return response.choices[0]["message"]["content"]

def thank_you(message):
    prompt = f"rephrase {message} with a warm tone."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are an assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0]["message"]["content"]

@app.route('/add_expense', methods=['POST'])
def add_expense():
    """Add an expense to the JSON data and predict the payer if not specified"""
    data = load_data('expenses.json')
    expense_data = request.json
    expense_type = expense_data.get('category')
    amount = expense_data.get('amount')
    payer = expense_data.get('payer', '').strip()

    if not expense_type or amount is None:
        return jsonify({'error': 'Category and amount are required'}), 400

    expense = {"type": expense_type, "amount": amount, "payer": payer}

    if not payer:
        payer = predict_payer(expense_type, amount, data)
        expense = {"type": expense_type, "amount": amount, "payer": payer, "confirmed": False}
        data.append(expense)
        save_data('expenses.json', data)
        return jsonify({'payer': payer, 'confirmed': False,
                        'message': f"A new bill for {expense_type} costing ${amount} just came in. {payer}, would you like to pay this bill?"})

    expense = {"type": expense_type, "amount": amount, "payer": payer, "confirmed": True}
    thank_you_message = f"Thank you {payer}, for agreeing to pay the {expense_type} bill of ${amount}. We appreciate it!"
    thank_you_message = thank_you(thank_you_message)
    return jsonify({'payer': payer, 'confirmed': True,
                    'message': thank_you_message})

@app.route('/confirm_payment', methods=['POST'])
def confirm_payment():
    data = request.json
    confirm = data.get('confirm')
    payer = data.get('payer')

    expenses = load_data('expenses.json')
    expense_type = expenses[-1]['type']
    amount = expenses[-1]['amount']
    # Assuming the last entry is the one to be confirmed
    if confirm:
        expenses[-1]['payer'] = payer  # Assign new payer
        expenses[-1]['confirmed'] = True

        save_data('expenses.json', expenses)
        thank_you_message = f"Thank you {payer}, for agreeing to pay the {expense_type} bill of ${amount}. We appreciate it!"
        thank_you_message = thank_you(thank_you_message)
        return jsonify({'message': thank_you_message})
        
# Static file serving
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static_file(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    app.run(debug=True)
