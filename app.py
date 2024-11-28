from flask import Flask, jsonify, request, abort

app = Flask(__name__)

users = {}
categories = {}
records = {}
accounts = {}
user_counter = 1
category_counter = 1
record_counter = 1


@app.route('/user', methods=['POST'])
def create_user():
    global user_counter
    data = request.get_json()
    if 'name' not in data:
        return jsonify({"error": "User name is required"}), 400
    user_id = user_counter
    users[user_id] = {"id": user_id, "name": data['name']}
    accounts[user_id] = {"user_id": user_id, "balance": 0}  # Створення рахунку
    user_counter += 1
    return jsonify(users[user_id]), 201


@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    if user_id not in users:
        return jsonify({"error": "User not found"}), 404
    user_data = users[user_id]
    user_data['account'] = accounts[user_id]  # Додаємо інформацію про рахунок
    return jsonify(user_data)


@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if user_id not in users:
        return jsonify({"error": "User not found"}), 404
    del users[user_id]
    del accounts[user_id]
    return jsonify({"message": "User deleted"}), 204


@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(list(users.values()))


@app.route('/account/<int:user_id>', methods=['GET'])
def get_account(user_id):
    if user_id not in accounts:
        return jsonify({"error": "Account not found"}), 404
    return jsonify(accounts[user_id])


@app.route('/account/<int:user_id>/add', methods=['POST'])
def add_to_account(user_id):
    if user_id not in accounts:
        return jsonify({"error": "Account not found"}), 404
    data = request.get_json()
    if 'amount' not in data or not isinstance(data['amount'], (int, float)) or data['amount'] <= 0:
        return jsonify({"error": "Valid amount is required"}), 400
    accounts[user_id]['balance'] += data['amount']
    return jsonify(accounts[user_id])


@app.route('/record', methods=['POST'])
def create_record():
    global record_counter
    data = request.get_json()
    if 'user_id' not in data or 'category_id' not in data or 'amount' not in data:
        return jsonify({"error": "Record must include user_id, category_id, and amount"}), 400
    if data['user_id'] not in users or data['category_id'] not in categories:
        return jsonify({"error": "User or category not found"}), 404
    if data['amount'] <= 0:
        return jsonify({"error": "Amount must be positive"}), 400

    user_id = data['user_id']
    amount = data['amount']

    # Перевірка балансу та автоматичне списання
    if accounts[user_id]['balance'] < amount:
        return jsonify({"error": "Insufficient funds"}), 400
    accounts[user_id]['balance'] -= amount

    record_id = record_counter
    records[record_id] = {
        "id": record_id,
        "user_id": user_id,
        "category_id": data['category_id'],
        "amount": amount,
        "timestamp": data.get("timestamp", "2024-11-06T00:00:00Z")
    }
    record_counter += 1
    return jsonify(records[record_id]), 201


@app.route('/record/<int:record_id>', methods=['GET'])
def get_record(record_id):
    if record_id not in records:
        return jsonify({"error": "Record not found"}), 404
    return jsonify(records[record_id])


@app.route('/record/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    if record_id not in records:
        return jsonify({"error": "Record not found"}), 404
    del records[record_id]
    return jsonify({"message": "Record deleted"}), 204


@app.route('/record', methods=['GET'])
def get_records():
    user_id = request.args.get('user_id', type=int)
    category_id = request.args.get('category_id', type=int)

    filtered_records = [
        record for record in records.values()
        if (user_id is None or record['user_id'] == user_id) and
           (category_id is None or record['category_id'] == category_id)
    ]

    if user_id is None and category_id is None:
        return jsonify({"error": "user_id or category_id parameter is required"}), 400

    return jsonify(filtered_records)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
