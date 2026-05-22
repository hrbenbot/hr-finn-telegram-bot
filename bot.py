from flask import Flask
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

TOKEN = "7987697105:AAHYg1LmBOyQlhrgLBp6gcwSinQj9te_sLg"

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "service_account.json",
    scope
)

client = gspread.authorize(creds)

spreadsheet = client.open("CV_DAU_DATABASE")
sheet_cv_dau = spreadsheet.worksheet("CV_DAU")
sheet_nhan_viec = spreadsheet.worksheet("NHAN_VIEC")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    data = {}

    lines = text.split("\n")
    for line in lines:
        if "：" in line:
            key, value = line.split("：", 1)
            data[key.strip()] = value.strip()
        elif ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()

    if "姓名" not in data:
        await update.message.reply_text("Thiếu 姓名, bot chưa lưu được.")
        return

    if "ngày nhận việc" in data:
        ngay_raw = data.get("ngày nhận việc", "")

        try:
            ngay_nhan_viec = datetime.strptime(ngay_raw, "%d-%m-%Y").strftime("%m月 %d， %Y")
        except:
            ngay_nhan_viec = ngay_raw

        row = [
            "",
            data.get("姓名", ""),
            "",
            "",
            "",
            data.get("性别", ""),
            "越南",
            data.get("岗位", ""),
            ngay_nhan_viec,
            ngay_nhan_viec,
            "TT",
            0,
            0,
            0,
            data.get("平台", "")
        ]

        next_row = len(sheet_nhan_viec.col_values(2)) + 1
        sheet_nhan_viec.update(f"A{next_row}:O{next_row}", [row])
        await update.message.reply_text("Đã lưu hồ sơ nhận việc.")
        return

    row = [
        "",
        data.get("姓名", ""),
        data.get("性别", ""),
        "越南",
        data.get("岗位", ""),
        datetime.now().strftime("%m月 %d， %Y"),
        "TT",
        0,
        0,
        data.get("平台", "")
    ]

    sheet_cv_dau.append_row(row)
    await update.message.reply_text("Đã lưu CV đậu.")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT, handle))

app.run_polling()
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "HR Finn Bot is running"

def run_web():
    web_app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web).start()

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, handle))
app.run_polling()