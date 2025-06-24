from gtts import gTTS
import MySQLdb.cursors
import uuid
import os

# DB接続
conn = MySQLdb.connect(
    host="localhost",
    user="test",
    password="Si150213",
    database="phrase_app",
    charset="utf8mb4",
    cursorclass=MySQLdb.cursors.DictCursor
)
cursor = conn.cursor()

# フレーズ取得
cursor.execute("SELECT id, jp FROM phrases WHERE audio_filename IS NULL OR audio_filename = ''")
phrases = cursor.fetchall()

os.makedirs("static/audio", exist_ok=True)

count_success = 0
count_fail = 0

for p in phrases:
    if not p['jp'].strip():
        continue

    if p['jp'] == "お会計は◯◯円です":
        safe_jp = "お会計は千円です"
    else:
        safe_jp = (
            p['jp']
            .replace("◯◯", "金額")
            .replace("××", "番号")
            .replace("●●", "内容")
        )

    try:
        tts = gTTS(text=safe_jp, lang="ja")
        filename = f"audio_{uuid.uuid4().hex[:8]}.mp3"
        filepath = os.path.join("static/audio", filename)
        tts.save(filepath)

        cursor.execute("UPDATE phrases SET audio_filename = %s WHERE id = %s", (filename, p['id']))
        conn.commit()
        count_success += 1
    except Exception as e:
        print(f"[NG] {p['jp']} - {e}")
        count_fail += 1

cursor.close()
conn.close()

print(f"音声生成完了：成功 {count_success} 件、失敗 {count_fail} 件")
