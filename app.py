
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "azar-secret"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///azar.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20), unique=True)
    role = db.Column(db.String(20))
    password = db.Column(db.String(50))

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    amount = db.Column(db.Integer, default=40000)
    total = db.Column(db.Integer, default=60000)
    status = db.Column(db.String(20), default="PENDING")
    guarantors = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    penalty = db.Column(db.Integer, default=0)
    collector = db.Column(db.String(50))

with app.app_context():
    db.create_all()
    if not User.query.filter_by(role="admin").first():
        db.session.add(User(name="Admin", phone="0700000000", role="admin", password="1234"))
        db.session.add(User(name="Collector", phone="0711111111", role="collector", password="1234"))
        db.session.commit()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/client/signup", methods=["GET", "POST"])
def client_signup():
    if request.method == "POST":
        u = User(
            name=request.form["name"],
            phone=request.form["phone"],
            password=request.form["password"],
            role="client"
        )
        db.session.add(u)
        db.session.commit()
        return redirect("/client/login")
    return render_template("client_signup.html")

@app.route("/client/login", methods=["GET", "POST"])
def client_login():
    if request.method == "POST":
        u = User.query.filter_by(
            phone=request.form["phone"],
            password=request.form["password"],
            role="client"
        ).first()
        if u:
            session["role"] = "client"
            return redirect("/client/apply")
    return render_template("client_login.html")

@app.route("/client/apply", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        l = Loan(
            client_name=request.form["name"],
            phone=request.form["phone"],
            guarantors=request.form["guarantors"]
        )
        db.session.add(l)
        db.session.commit()
        return render_template("agreement.html", loan=l)
    return render_template("apply.html")

@app.route("/staff/login", methods=["GET", "POST"])
def staff_login():
    if request.method == "POST":
        u = User.query.filter_by(
            phone=request.form["phone"],
            password=request.form["password"]
        ).first()
        if u:
            session["role"] = u.role
            return redirect("/admin" if u.role == "admin" else "/collector")
    return render_template("staff_login.html")

@app.route("/admin")
def admin():
    loans = Loan.query.all()
    return render_template("admin.html", loans=loans)

@app.route("/approve/<int:id>", methods=["POST"])
def approve(id):
    l = Loan.query.get_or_404(id)
    l.status = "APPROVED"
    db.session.commit()
    return redirect("/admin")

@app.route("/waive/<int:id>")
def waive(id):
    l = Loan.query.get_or_404(id)
    l.penalty = 0
    db.session.commit()
    return redirect("/admin")

@app.route("/collector")
def collector():
    loans = Loan.query.all()
    return render_template("collector.html", loans=loans)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
