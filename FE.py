from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import requests
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

API_URL = 'http://localhost:5000'  # Backend API

# Home (Login) Page
@app.route('/')
def home():
    return render_template('login.html')

# Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        response = requests.post(f'{API_URL}/register', json={'username': username, 'email': email, 'password': password})
        
        if response.status_code == 201:
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('home'))
        
        flash('Registration failed. Email may already be in use.', 'error')
        return redirect(url_for('register'))
    
    return render_template('register.html')

# Login Route
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    
    response = requests.post(f'{API_URL}/login', json={'email': email, 'password': password})
    
    if response.status_code == 200:
        session['token'] = response.json()['token']
        flash('Login successful!', 'success')
        return redirect(url_for('search'))
    
    flash('Invalid email or password. Please try again.', 'error')
    return redirect(url_for('home'))

# Logout Route
@app.route('/logout')
def logout():
    session.pop('token', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Search Books
@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'token' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('home'))
    
    books = []
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if not query:
            flash('Please enter a search term.', 'error')
            return redirect(url_for('search'))
        
        headers = {'Authorization': f'Bearer {session["token"]}'}
        response = requests.get(f'{API_URL}/search', params={'query': query}, headers=headers)
        
        if response.status_code == 200:
            books = response.json().get('items', [])
        else:
            flash('Failed to fetch books. Please try again.', 'error')
    
    return render_template('search.html', books=books)

# Submit Review
@app.route('/review', methods=['POST'])
def review():
    if 'token' not in session:
        flash('Please log in to submit a review.', 'error')
        return redirect(url_for('home'))
    
    book_id = request.form.get('book_id')
    review_text = request.form.get('review', '').strip()
    rating = request.form.get('rating')
    
    if not book_id or not review_text or not rating:
        flash('All fields are required.', 'error')
        return redirect(url_for('search'))
    
    headers = {'Authorization': f'Bearer {session["token"]}'}
    response = requests.post(f'{API_URL}/review', json={'bookId': book_id, 'review': review_text, 'rating': rating}, headers=headers)
    
    if response.status_code == 201:
        flash('Review submitted successfully!', 'success')
    else:
        flash('Failed to submit review. Please try again.', 'error')
    
    return redirect(url_for('search'))

if __name__ == '__main__':
    app.run(debug=True, port=3000)
