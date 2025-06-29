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
    messages = Message.query.all()
    return jsonify([message.to_dict() for message in messages])


@app.route('/messages/<int:id>')
def messages_by_id(id):
    message = db.session.get(Message, id)
    if message:
        return jsonify(message.to_dict())
    else:
        return "<h1>Message not found<h1/>"

if __name__ == '__main__':
    app.run(port=5555)
    

@app.route('/messages', methods=["POST"])
def post_message():
    data = request.get_json()

    if not data or 'body' not in data or 'username' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    new_message = Message(
        body=data['body'],
        username=data['username'],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.session.add(new_message)
    db.session.commit()

    return jsonify(new_message.to_dict()), 201

@app.route('/messages/<int:id>', methods=["PATCH"])
def update_message(id):
    message = db.session.get(Message, id)

    if not message:
        return jsonify({"error": "Message not found"}), 404

    data = request.get_json()

    if 'body' in data:
        message.body = data['body']
    if 'username' in data:
        message.username = data['username']

    message.updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify(message.to_dict()), 200

@app.route('/messages/<int:id>', methods=["DELETE"])
def delete_message(id):
    message = db.session.get(Message, id)

    if not message:
        return jsonify({"error": "Message not found"}), 404

    db.session.delete(message)
    db.session.commit()

    return jsonify({"message": f"Message {id} deleted successfully"}), 200
