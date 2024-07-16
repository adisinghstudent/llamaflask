from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.urls import url_parse
from models import db, User
from config import Config
from langchain_community.llms import Ollama

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

llm = Ollama(model="llama3")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('chat')
        return redirect(next_page)
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    message = request.json['message']
    # Here you would typically save the message to a database
    # For simplicity, we're just echoing it back with the AI response
    ai_response = llm.invoke(message)
    return jsonify({'user_message': message, 'ai_response': ai_response})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)