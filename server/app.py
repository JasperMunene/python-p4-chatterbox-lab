from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages')
def messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return jsonify([message.to_dict() for message in messages])

@app.route('/messages', methods=['POST'])
def create_message():
    body = request.json.get('body')
    username = request.json.get('username')

    if not body or not username:
        return make_response(jsonify({"error": "Missing 'body' or 'username'"}), 400)

    new_message = Message(body=body, username=username, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    db.session.add(new_message)
    db.session.commit()

    return jsonify(new_message.to_dict()), 201

@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.get(id)
    if not message:
        return make_response(jsonify({"error": "Message not found"}), 404)

    body = request.json.get('body')
    if not body:
        return make_response(jsonify({"error": "Missing 'body'"}), 400)

    message.body = body
    message.updated_at = datetime.utcnow()  # Update the timestamp
    db.session.commit()

    return jsonify(message.to_dict())

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get(id)
    if not message:
        return make_response(jsonify({"error": "Message not found"}), 404)

    db.session.delete(message)
    db.session.commit()

    return jsonify({"message": "Message deleted successfully"}), 200


@app.route('/messages/<int:id>', methods=['GET'])
def messages_by_id(id):
    message = Message.query.get(id)  # Retrieve the message by ID
    if not message:
        return make_response(jsonify({"error": "Message not found"}), 404)

    return jsonify(message.to_dict())  # Return the message as JSON


if __name__ == '__main__':
    app.run(port=5555)
