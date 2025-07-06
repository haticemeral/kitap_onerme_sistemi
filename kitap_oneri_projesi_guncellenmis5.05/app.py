from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os  
from model import recommend_books  

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kitaplar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.session_protection = "strong"
login_manager.login_message = "Lütfen giriş yapın!"

# Kullanıcı Modeli
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


# Kitap Modeli
class Kitap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100), nullable=False)
    yazar = db.Column(db.String(100), nullable=False)
    tur = db.Column(db.String(50))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) if user_id else None


@app.route('/')
def index():
    return redirect(url_for('login'))



@app.route("/recommend", methods=["POST"])
@login_required
def recommend():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Geçersiz veri!"}), 400

        book_title = data.get("title", "").strip()
        if not book_title:
            return jsonify({"error": "Kitap adı gerekli!"}), 400

        recommendations = recommend_books(book_title)
        if not recommendations:
            return jsonify({"message": "Öneri bulunamadı."}), 404

        return jsonify(recommendations)

    except Exception as e:
        return jsonify({"error": f"Sunucu hatası: {str(e)}"}), 500


# Giriş Yönlendirmesi
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        
        return render_template('login.html', error='Geçersiz kullanıcı adı veya şifre!')
    
    return render_template('login.html')

# Kayıt Yönlendirmesi
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/home')
@login_required
def home():
    return render_template('index.html')  


# Çıkış Yönlendirmesi
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
# Hesap Sayfası
@app.route('/account')
@login_required
def account():
    return render_template('account.html', user=current_user)
# İletişim sayfası
@app.route('/iletisim')
def iletisim():
    return render_template('iletisim.html') 
# About sayfası
@app.route('/about')
def about():
    return render_template('about.html') 
# Kitap sayfası
@app.route('/kitap')
def kitap():
    return render_template('kitaplar.html')
#etkinlik sayfası
@app.route('/etkinlik')
def etkinlik():
    return render_template('etkinlik.html') 
# Veritabanı
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)









