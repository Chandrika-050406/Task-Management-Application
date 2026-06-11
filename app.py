from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO users(username, email, password)
            VALUES (?, ?, ?)
            """,
            (username, email, password)
        )

        conn.commit()
        conn.close()

        return "Registration Successful!"

    return render_template('register.html')


if __name__ == '__main__':
    from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

app.secret_key = "my_secret_key"


@app.route('/')
def home():
    return redirect('/login')


# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO users(username,email,password)
            VALUES(?,?,?)
            """,
            (username, email, password)
        )

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        print("Email entered:", repr(email))
        print("Password entered:", repr(password))

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()

        print("User found:", user)

        conn.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]

            return redirect('/dashboard')

        return "Invalid Email or Password"

    return render_template('login.html')
    # DASHBOARD
@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM tasks
        WHERE user_id=?
        """,
        (session['user_id'],)
    )

    tasks = cursor.fetchall()

    conn.close()

    # Statistics
    total_tasks = len(tasks)

    completed_tasks = len(
        [task for task in tasks if task[4] == 'Completed']
    )

    pending_tasks = len(
        [task for task in tasks if task[4] == 'Pending']
    )

    return render_template(
        'dashboard.html',
        tasks=tasks,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks
    )
@app.route('/add_task', methods=['GET', 'POST'])
def add_task():

    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':

        title = request.form['title']
        description = request.form['description']
        status = request.form['status']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO tasks(user_id, title, description, status)
            VALUES (?, ?, ?, ?)
            """,
            (session['user_id'], title, description, status)
        )

        conn.commit()
        conn.close()

        return redirect('/dashboard')

    return render_template('add_task.html')

@app.route('/delete_task/<int:id>')
def delete_task(id):

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM tasks
        WHERE id=? AND user_id=?
        """,
        (id, session['user_id'])
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')

@app.route('/edit_task/<int:id>', methods=['GET', 'POST'])
def edit_task(id):

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':

        title = request.form['title']
        description = request.form['description']
        status = request.form['status']

        cursor.execute(
            """
            UPDATE tasks
            SET title=?, description=?, status=?
            WHERE id=? AND user_id=?
            """,
            (
                title,
                description,
                status,
                id,
                session['user_id']
            )
        )

        conn.commit()
        conn.close()

        return redirect('/dashboard')

    cursor.execute(
        """
        SELECT * FROM tasks
        WHERE id=? AND user_id=?
        """,
        (id, session['user_id'])
    )

    task = cursor.fetchone()

    conn.close()

    return render_template(
        'edit_task.html',
        task=task
    )
    

# LOGOUT
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)