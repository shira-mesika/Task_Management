from flask import Flask, render_template, url_for, request, redirect
import sqlite3
# create an app
app = Flask(__name__)


# STEP 1: DATABASE
# create a connection to database:
def get_db_connection():
    connection = sqlite3.connect('tasks.db')
    connection.row_factory = sqlite3.Row  # access to row values by column name
    return connection


# create table
def create_table():
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                completed BOOLEAN NOT NULL DEFAULT 0)''')
        connection.commit()


# STEP 2: Define the routes:
# home page:  show all the tasks
@app.route("/")
@app.route("/home")
def show_all_tasks():
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM tasks')
        tasks = cursor.fetchall()
    return render_template('show_all.html', tasks=tasks)


@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        completed = '1' if 'completed' in request.form else '0'
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("""
                    INSERT INTO tasks (title, description, completed) VALUES (?, ?, ?)""",
                           (title, description, completed))
            connection.commit()
        return redirect(url_for('show_all_tasks'))
    return render_template('add_task.html')


@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        connection.commit()
    return redirect(url_for('show_all_tasks'))


@app.route('/toggle_complete/<int:task_id>')
def toggle_complete(task_id):
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT completed FROM tasks WHERE id = ?', (task_id,))
        task = cursor.fetchone()
        if task:  # switch the status
            new_status = not task['completed']
            cursor.execute('UPDATE tasks SET completed = ? WHERE id = ?', (new_status, task_id))
            connection.commit()
    return redirect(url_for('show_all_tasks'))


@app.route('/update_task/<int:task_id>', methods=['GET', 'POST'])
def update_task(task_id):
    with get_db_connection() as connection:
        cursor = connection.cursor()
        # take the task details from database:
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        task = cursor.fetchone()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        completed = '1' if 'completed' in request.form else '0'

        # update the task with the new details
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute('''
                UPDATE tasks SET title = ?, description = ?, completed = ?
                WHERE id = ?''', (title, description, completed, task_id))
            connection.commit()
        return redirect(url_for('show_all_tasks'))
    return render_template('update_task.html', task=task)


if __name__ == '__main__':
    create_table()
    app.run(debug=True)
