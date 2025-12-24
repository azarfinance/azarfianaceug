from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import csv, os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

loans = []

@app.route('/')
def index():
    return render_template('index.html', loans=loans)

@app.route('/create_loan', methods=['POST'])
def create_loan():
    client_name = request.form.get('client_name')
    amount = request.form.get('amount')
    loan = {'id': len(loans)+1, 'client_name': client_name, 'amount': amount, 'date': datetime.now(), 'status': 'pending'}
    loans.append(loan)
    flash('Loan created successfully!')
    return redirect(url_for('index'))

@app.route('/approve_loan/<int:loan_id>', methods=['POST'])
def approve_loan(loan_id):
    pin = request.form.get('pin')
    if pin != '1234':
        flash('Invalid admin PIN!')
    else:
        for loan in loans:
            if loan['id'] == loan_id:
                loan['status'] = 'approved'
                flash('Loan approved!')
                break
    return redirect(url_for('index'))

@app.route('/collect/<int:loan_id>', methods=['POST'])
def collect(loan_id):
    for loan in loans:
        if loan['id'] == loan_id:
            loan['status'] = 'collected'
            flash('Loan collected!')
            break
    return redirect(url_for('index'))

@app.route('/export_csv')
def export_csv():
    csv_file = os.path.join('loans_export.csv')
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID','Client','Amount','Date','Status'])
        for loan in loans:
            writer.writerow([loan['id'], loan['client_name'], loan['amount'], loan['date'], loan['status']])
    flash('CSV exported!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
