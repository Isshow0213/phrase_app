from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
import os
import MySQLdb.cursors
from gtts import gTTS
import uuid
from datetime import datetime, timedelta

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
    user_id = session['user_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # 検索条件組み立てはそのまま
    where_clause = "(p.user_id IS NULL OR p.user_id = %s) AND is_deleted = 0"
    params = [user_id]
    if q:
        like_q = f"%{q}%"
        where_clause += " AND (p.jp LIKE %s OR p.en LIKE %s OR p.ne LIKE %s) AND is_deleted = 0"
        params += [like_q, like_q, like_q]

    # フレーズ本体 + is_favorite フラグを取得
    sql = f"""
      SELECT
        p.id, p.category, p.jp, p.en, p.ne, p.audio_filename,
        EXISTS(
          SELECT 1 FROM favorites f
          WHERE f.user_id = %s
            AND f.phrase_id = p.id
        ) AS is_favorite
      FROM phrases p
      WHERE {where_clause}
      ORDER BY p.category, p.jp
    """
    # user_id はサブクエリ用にももう一度渡す
    cursor.execute(sql, [user_id] + params)
    phrases = cursor.fetchall()
    cursor.close()

    return render_template(
      'index.html',
      phrases=phrases,
      query=q,
      username=session['username']
    )


@app.route("/delete/<int:id>", methods=["POST"])
def delete_phrase(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("SELECT * FROM phrases where id = %s", (id,))
    phrase = cursor.fetchone()

    if phrase["user_id"] is None:
        flash("共通フレーズは削除できません")
        return redirect(url_for("index"))

    cursor.execute("""UPDATE phrases SET is_deleted=1, deleted_at=%s
                   WHERE id=%s
                   """, (datetime.now(), id))
    mysql.connection.commit()
    cursor.close()
    flash("フレーズを削除しました")
    return redirect(url_for("index"))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

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

from flask import request, redirect, url_for

@app.route('/favorite/<int:phrase_id>', methods=['POST'])
def toggle_favorite(phrase_id):
    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    cursor.execute(
        "SELECT 1 FROM favorites WHERE user_id=%s AND phrase_id=%s",
        (user_id, phrase_id)
    )
    if cursor.fetchone():
        cursor.execute(
          "DELETE FROM favorites WHERE user_id=%s AND phrase_id=%s",
          (user_id, phrase_id)
        )
        new_val = False
    else:
        cursor.execute(
          "INSERT INTO favorites (user_id, phrase_id) VALUES (%s, %s)",
          (user_id, phrase_id)
        )
        new_val = True

    mysql.connection.commit()
    cursor.close()

    return jsonify({'is_favorite': new_val})


@app.route('/favorite', methods=['GET'])
def show_favorite():
    user_id = session['user_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    sql = """
      SELECT p.*
      FROM phrases p
      JOIN favorites f
        ON f.phrase_id = p.id
       AND f.user_id   = %s
      ORDER BY p.category, p.jp
    """
    cursor.execute(sql, (user_id,))
    phrases = cursor.fetchall()
    cursor.close()

    for p in phrases:
        p['is_favorite'] = 1

    return render_template(
      "favorite.html",
      phrases=phrases,
      username=session['username']
    )

@app.route("/deleted", methods=["GET"])
def show_deleted_phrases():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("""
        SELECT * FROM phrases
        WHERE is_deleted = 1
            AND (user_id IS NULL OR user_id = %s)
        ORDER BY deleted_at DESC
        LIMIT 30
    """, (user_id,))

    phrases = cursor.fetchall()
    cursor.close()

    return render_template(
        "deleted.html",
        phrases=phrases,
        username=session["username"]
    )

@app.route("/restore/<int:phrase_id>", methods=["POST"])
def restore_phrase(phrase_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""UPDATE phrases SET is_deleted=0, deleted_at=NULL
                    WHERE id=%s""", (phrase_id, ))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for("show_deleted_phrases"))

@app.before_request
def delete_old_phrases_on_start():
    cursor = mysql.connection.cursor()
    cutoff = datetime.now() - timedelta(days=30)
    cursor.execute("""
                    DELETE FROM phrases
                    WHERE is_deleted = 1 AND deleted_at < %s
                """, (cutoff,))
    mysql.connection.commit()
    cursor.close()


if __name__ == "__main__":
    app.run(debug=True)
