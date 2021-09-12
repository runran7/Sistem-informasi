from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import firebase_admin
from firebase_admin import credentials, firestore
from functools import wraps
import requests
from requests.structures import CaseInsensitiveDict

cred = credentials.Certificate('firebase.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)
app.secret_key = "barusaja"

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwarg):
        if 'user' in session:
            return f(*arg, **kwarg)
        else:
            flash('anda harus login', 'danger')
            return redirect(url_for('login'))
    return wrapper

def send_wa(m, p):
    api = "77590e2588a4f6fe8800aa1681eee8a1ff886f33"
    url = "https://starsender.online/api/sendText"

    data = {
        "tujuan": p,
        "messege": m
    }

    headers = CaseInsensitiveDict()
    headers["apikey"] = api

    res = requests.post(url, json=data, headers=headers)
    print(res-text)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/tambah_data')
def tambah_data():
    data = {
        "name": "amhad",
        "email": "baba@gmail.com",
        "nim": "6475838",
        "jurusan": "manajemen"
    }

    db.collection("users").document().set(data)
    return "berhasil login"


@app.route('/login', methods=["GET", "POST"])
def login():
    # menentukan method
    if request.method == "POST":

        # ambil data dari form
        data = {
            "email": request.form["email"],
            "password": request.form["password"]
        }
        # lakukan pengecekan
        users = db.collection('users').where("email", "==", data["email"]).stream()
        user = {}

        for us in users:
            user = us.to_dict()

        if user:
            if check_password_hash(user["password"], data["password"]):
                session["user"] = user
                flash('selamat anda berhasil login', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('maaf password anda salah', 'danger')
                return redirect(url_for('login'))
        else:
            flash('email belum terdaftar', 'danger')
            return redirect(url_for('login'))
    if 'user' in session:
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('anda belum login', "danger")
        return redirect(url_for('login'))

    return render_template("dashboard.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/mahasiswa')
def mahasiswa():
    maba = db.collection("mahasiwa").stream()
    mb = []

    for mhs in maba:
        m = mhs.to_dict()
        m["id"] = mhs.id
        mb.append(m)

    return render_template('mahasiswa.html', data=mb)


@app.route('/mahasiswa/tambah', methods=["GET", "POST"])
def tambah_mhs():
    if request.method == 'POST':
        data = {
            "nama": request.form["nama"],
            "email": request.form["email"],
            "nim": request.form["nim"],
            "jurusan": request.form["jurusan"]
        }

        db.collection("mahasiwa").document().set(data)
        send_wa(f"Halo *{data['nama_lengkap']}* Selamat siang", data["no_hp"])
        flash("Yey Berhasil", "success")
        return redirect(url_for('mahasiswa'))
    return render_template("add_mhs.html")


@app.route('/mahasiswa/hapus/<uid>')
def hapus_mhs(uid):
    db.collection('mahasiwa').document(uid).delete()
    flash("Hilang Sudah", "danger")
    return redirect(url_for('mahasiswa'))


@app.route('/mahasiswa/lihat/<uid>')
def lihat_mhs(uid):
    user = db.collection('mahasiwa').document(uid).get().to_dict()
    return render_template('lihat_mhs.html', user=user)


@app.route('/mahasiswa/ubah/<uid>', methods=["GET", "POST"])
def ubah_mhs(uid):
    if request.method == "POST":
        data = {
            "nama": request.form["nama"],
            "email": request.form["email"],
            "nim": request.form["nim"],
            "jurusan": request.form["jurusan"]
        }

        db.collection('mahasiwa').document(uid).set(data, merge=True)
        return redirect(url_for('mahasiswa'))

    user = db.collection('mahasiwa').document(uid).get().to_dict()
    user['id'] = uid
    return render_template('ubah_mhs.html', user=user)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = {
            "nama_lengkap": request.form["nama_lengkap"],
            "email": request.form["email"],
            "no_hp": request.form["no_hp"]
        }
        
        users = db.collection('users').where('email', '==', data['email']).stream()
        user = {}
        for us in users:
            user = us.to_dict()
        if user:
            flash('Email Sudah Terdaftar', 'danger')
            return redirect(url_for('register'))
    
        data['password'] = generate_password_hash(request.form['password'], 'sha256')
    
        db.collection('users').document().set(data)
        flash('Berhasil Register', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

if __name__ == "__main__":
    app.run(debug=True)
