from idlelib.pyparse import trans

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
import os
import MySQLdb.cursors
from gtts import gTTS
import uuid
from datetime import datetime, timedelta

translations = {
    'ja': {
        'welcome': 'ようこそ',
        'logout': 'ログアウト',
        'add_phrase': 'フレーズ追加',
        'search_placeholder': 'キーワードで絞り込む',
        'search_button': '検索',
        'search_reset': '← 全件表示に戻る',
        'no_results': '該当するフレーズがありません。',
        'search_result': '「{query}」 の検索結果：{count} 件',
        'reset_search': '← 全件表示に戻る',
        "add_phrase_title": "フレーズを追加",
        "form_header": "フレーズ追加フォーム",
        "back_to_list": "← 一覧に戻る",
        "category": "カテゴリ：",
        "select_prompt": "-- 選択してください --",
        "guide": "案内",
        "payment": "支払い",
        "thanks": "お礼",
        "other": "その他",
        "jp_label": "日本語：",
        "en_label": "英語：",
        "ne_label": "ネパール語：",
        "audio_label": "音声ファイル（任意）：",
        "audio_note": "オーディオファイルを入れなくても自動で生成されます",
        "submit_button": "フレーズを保存",
        "deleted_title": "最近削除されたフレーズ",
        "back_to_index": "← 戻る",
        "restore_button": "復元",
        "no_deleted": "削除されたフレーズがありません。",
        "login_title": "ログイン",
        "username_label": "ユーザー名：",
        "password_label": "パスワード：",
        "login_button": "ログイン",
        "register_link": "新規登録",
        "favorite_title": "お気に入り一覧",
        "no_favorite": "まだお気に入りはありません。",
        "confirm_delete": "削除しますか？",
        "delete_success": "フレーズを削除しました",
        "delete_forbidden": "共通フレーズは削除できません",
        "login_failed": "ユーザー名またはパスワードが間違っています",
        "register_exists": "このユーザー名はすでに使われています",
        "register_success": "登録が完了しました。ログインしてください。",
        "register_title": "新規ユーザー登録",
        "username": "ユーザー名",
        "password": "パスワード",
        "register_button": "登録",
        "already_have_account": "既にアカウントをお持ちの方はこちら"
    },
    'ne': {
        'welcome': 'स्वागत छ',
        'logout': 'लगआउट',
        'add_phrase': 'फ्रेज थप्नुहोस्',
        'search_placeholder': 'कीवर्ड अनुसार खोज्नुहोस्',
        'search_button': 'खोज्नुहोस्',
        'search_reset': '← सबै देखाउनुहोस्',
        'no_results': 'उपयुक्त फ्रेज फेला परेनन्।',
        'search_result': '「{query}」 को खोज परिणाम: {count} वटा',
        'reset_search': '← सबै देखाउनेमा फर्कनुहोस्',
        "add_phrase_title": "फ्रेज थप्नुहोस्",
        "form_header": "फ्रेज थप्ने फारम",
        "back_to_list": "← सूचीमा फर्कनुहोस्",
        "category": "श्रेणी：",
        "select_prompt": "-- कृपया चयन गर्नुहोस् --",
        "guide": "मार्गदर्शन",
        "payment": "भुक्तानी",
        "thanks": "धन्यवाद",
        "other": "अन्य",
        "jp_label": "जापानी：",
        "en_label": "अंग्रेजी：",
        "ne_label": "नेपाली：",
        "audio_label": "अडियो फाइल (वैकल्पिक)：",
        "audio_note": "यदि अडियो अपलोड नगरे पनि स्वचालित रूपमा生成 हुन्छ",
        "submit_button": "फ्रेज सुरक्षित गर्नुहोस्",
        "deleted_title": "हालै मेटाइएका फ्रेजहरू",
        "back_to_index": "← पछाडि फर्कनुहोस्",
        "restore_button": "पुनर्स्थापना गर्नुहोस्",
        "no_deleted": "मेटाइएका फ्रेजहरू फेला परेनन्।",
        "login_title": "लगइन",
        "username_label": "प्रयोगकर्ता नाम：",
        "password_label": "पासवर्ड：",
        "login_button": "लगइन गर्नुहोस्",
        "register_link": "नयाँ दर्ता",
        "favorite_title": "मनपर्ने फ्रेजहरू",
        "no_favorite": "अहिलेसम्म कुनै मनपर्ने फ्रेज छैन।",
        "confirm_delete": "मेटाउन निश्चित हुनुहुन्छ?",
        "delete_success": "फ्रेज मेटाइयो",
        "delete_forbidden": "साझा फ्रेज मेटाउन मिल्दैन",
        "login_failed": "प्रयोगकर्ता नाम वा पासवर्ड गलत छ",
        "register_exists": "यो प्रयोगकर्ता नाम पहिले नै प्रयोगमा छ",
        "register_success": "दर्ता सफल भयो। लग इन गर्नुहोस्।",
        "register_title": "नयाँ प्रयोगकर्ता दर्ता",
        "username": "प्रयोगकर्ता नाम",
        "password": "पासवर्ड",
        "register_button": "दर्ता गर्नुहोस्",
        "already_have_account": "पहिले नै खाता छ? यहाँ क्लिक गर्नुहोस्"
    }
}


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

    lang = session.get("lang", "ja")
    t = translations[lang]
    return render_template('add.html', t=t, lang=lang)


import MySQLdb.cursors

@app.route('/home', methods=['GET'])
def index():

    lang = request.args.get("lang")
    if lang:
        session["lang"] = lang
    lang = session.get("lang", "ja")

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
        username=session['username'],
        lang=lang,
        t=translations[lang]
    )


@app.route("/delete/<int:id>", methods=["POST"])
def delete_phrase(id):
    lang = session.get("lang", "ja")
    t = translations[lang]

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
    flash(t["delete_success"])
    return redirect(url_for("index"))



@app.route('/login', methods=['GET', 'POST'])
def login():
    lang = session.get("lang", "ja")
    t = translations[lang]

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
            flash(t["login_failed"])

    return render_template('login.html', t=t, lang=lang)

@app.route('/register', methods=['GET', 'POST'])
def register():
    lang = session.get("lang", "ja")
    t = translations[lang]

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash(t["register_exists"])
            cursor.close()
            return render_template('register.html')

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        cursor.close()

        flash(t["register_success"])
        return redirect(url_for('login'))

    return render_template('register.html', t=t, lang=lang)


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

    lang = session.get("lang", "ja")
    t = translations[lang]

    return render_template(
        "favorite.html",
        phrases=phrases,
        username=session['username'],
        t=t,
        lang=lang
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

    lang = session.get("lang", "ja")
    t = translations[lang]

    return render_template(
        "deleted.html",
        phrases=phrases,
        username=session["username"],
        lang=lang,
        t=t
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

@app.route("/set-language/<lang_code>")
def set_language(lang_code):
    if lang_code in ["ja", "ne"]:
        session["lang"] = lang_code
    else:
        session["lang"] = "ja"
    return redirect(url_for("login"))

@app.route('/')
def choose_language():
    return render_template('language_select.html')




if __name__ == "__main__":
    app.run(debug=True)
