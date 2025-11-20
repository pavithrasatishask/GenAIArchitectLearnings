from flask import Flask, jsonify, request

app = Flask(__name__)

transactions = []
transaction_counter = 1

@app.route('/categories/expense')
def expense_categories():
    categories = [
        'Food & Drink', 'Shopping', 'Transport', 'Home', 'Bills & Fees',
        'Entertainment', 'Car', 'Travel', 'Family & Personal', 'Groceries', 'Other'
    ]
    return jsonify(categories)

@app.route('/categories/income')
def income_categories():
    categories = ['Salary', 'Gift', 'Bonus', 'Other']
    return jsonify(categories)

@app.route('/transaction', methods=['POST'])
def add_transaction():
    global transaction_counter
    data = request.json
    data['id'] = transaction_counter
    transaction_counter += 1
    transactions.append(data)
    return jsonify({"status": "success", "id": data['id']})

@app.route('/transaction', methods=['GET'])
def get_transactions():
    return jsonify(transactions)

@app.route('/transaction/<int:tx_id>', methods=['PUT'])
def update_transaction(tx_id):
    data = request.json
    for i, tx in enumerate(transactions):
        if tx.get('id') == tx_id:
            transactions[i].update(data)
            return jsonify({"status": "success"})
    return jsonify({"status": "failure", "message": "Transaction not found"}), 404

@app.route('/transaction/<int:tx_id>', methods=['DELETE'])
def delete_transaction(tx_id):
    global transactions
    transactions = [tx for tx in transactions if tx.get('id') != tx_id]
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
