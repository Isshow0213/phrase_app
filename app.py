from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import os
import MySQLdb.cursors
from gtts import gTTS
import uuid

app = Flask(__name__)
app.secret_key = 'Si150213'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'test'
app.config['MYSQL_PASSWORD'] = 'Si150213'
app.config['MYSQL_DB'] = 'phrase_app'
app.config['MYSQL_CHARSET'] = 'utf8mb4'

UPLOAD_FOLDER = os.path.join('static', 'audio')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



mysql = MySQL(app)

@app.route('/add', methods=['GET', 'POST'])
def add_phrase():

    if request.method == 'POST':
        category = request.form['category']
        jp = request.form['ja']
        en = request.form['en']
        ne = request.form['ne']

        tts = gTTS(text=jp, lang="ja")
        filename = f"audio_{uuid.uuid4().hex[:8]}.mp3"
        audio_path = os.path.join("static/audio", filename)
        tts.save(audio_path)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        user_id = session.get('user_id', None)
        cursor.execute("""
                    INSERT INTO phrases(category, jp, en, ne, audio_filename, user_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (category, jp, en, ne, filename, user_id))

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('index'))

    return render_template('add.html')

import MySQLdb.cursors
@app.route('/', methods=['GET'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    q = request.args.get('q', '').strip()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    user_id = session['user_id']
    # まずはユーザー絞り込み条件を括弧でグルーピング
    where_clause = "(user_id IS NULL OR user_id = %s)"
    params = [user_id]

    # キーワード検索が入っていれば、ANDでつなぐ
    if q:
        like_q = f"%{q}%"
        where_clause += " AND (jp LIKE %s OR en LIKE %s OR ne LIKE %s)"
        params += [like_q, like_q, like_q]

    sql = f"""
        SELECT id, category, jp, en, ne, audio_filename 
        FROM phrases
        WHERE {where_clause}
        ORDER BY category, jp
    """
    cursor.execute(sql, params)
    phrases = cursor.fetchall()
    cursor.close()

    return render_template('index.html',
                           phrases=phrases,
                           query=q,
                           username=session['username'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            flash("ユーザー名またはパスワードが間違っています")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("このユーザー名はすでに使われています")
            cursor.close()
            return render_template('register.html')

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        cursor.close()

        flash("登録が完了しました。ログインしてください。")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)