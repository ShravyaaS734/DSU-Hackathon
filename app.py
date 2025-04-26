import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = 'users.db'

def get_db():
    """Gets the database connection."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Closes the database connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initializes the database schema."""
    with app.app_context():
        db = get_db()
        try:
            with app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()
        except Exception as e:
            print(f"Error initializing database: {e}")
            db.rollback()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.route('/')
def index():
    """Renders the login page."""
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration."""
    if request.method == 'POST':
        username = request.form['new_username']
        password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('register.html', registration_error="Passwords do not match")

        db = get_db()
        error = None
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
                'SELECT id FROM users WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = f'User {username} is already registered.'

        if error is None:
            try:
                hashed_password = generate_password_hash(password)
                user_id = db.execute(
                    'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                    (username, hashed_password)
                ).lastrowid
                db.commit()
                session['user_id'] = user_id
                return redirect(url_for('options'))
            except Exception as e:
                db.rollback()
                error = f"Error registering user: {e}"
                return render_template('register.html', registration_error=error)
        else:
            return render_template('register.html', registration_error=error)

    return render_template('register.html')

@app.route('/info/<int:user_id>', methods=['GET', 'POST'])
def info(user_id):
    """Handles user information input (optional)."""
    if request.method == 'POST':
        yearly_income = request.form['yearly_income']
        business_type = request.form['business_type']
        marketing_strategy = request.form['marketing_strategy']

        db = get_db()
        try:
            db.execute(
                'UPDATE users SET yearly_income = ?, business_type = ?, marketing_strategy = ? WHERE id = ?',
                (yearly_income, business_type, marketing_strategy, user_id)
            )
            db.commit()
            return redirect(url_for('options'))  # Redirect to options after info update
        except Exception as e:
            db.rollback()
            error = f"Error updating user info: {e}"
            return render_template('info.html', error=error)

    return render_template('info.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

        if user is None or not check_password_hash(user['password_hash'], password):
            error = 'Invalid username or password'
        else:
            session['user_id'] = user['id']
            return redirect(url_for('options'))
    return render_template('login.html', error=error)

@app.route('/options/')
def options():
    """Renders the menu options page."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('options.html')

@app.route('/finmenu')
def finmenu():
    """Renders the login page."""
    return render_template('finmenu.html')

@app.route('/foremenu')
def foremenu():
    """Renders the login page."""
    return render_template('foremenu.html')

@app.route('/dashboard')
def dashboard():
    """Placeholder for a dashboard route (optional)."""
    if 'user_id' in session:
        db = get_db()
        user = db.execute('SELECT username FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        if user:
            return f'Logged in as {user["username"]}'
        else:
            return redirect(url_for('login'))
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    """Logs the user out."""
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.teardown_appcontext
def teardown_db(e):
    """Closes the database connection when the app context is torn down."""
    close_db()

if __name__ == '__main__':
    app.run(debug=True)