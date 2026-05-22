from flask import Flask
import threading
import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

TOKEN = "7987697105:AAHYg1LmBOyQlhrgLBp6gcwSinQj9te_sLg"

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])

creds = Credentials.from_service_account_info(
    service_account_info,
    scopes=scope
)

client = gspread.authorize(creds)

spreadsheet = client.open("CV_DAU_DATABASE")
sheet_cv_dau = spreadsheet.worksheet("CV_DAU")
sheet_nhan_viec = spreadsheet.worksheet("NHAN_VIEC")


def format_date(raw_date):
    try:
        return datetime.strptime(raw_date.strip(), "%d-%m-%Y").strftime("%m月 %d， %Y")
    except:
        return raw_date


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    data = {}

    for line in text.split("\n"):
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
        ngay_nhan_viec = format_date(data.get("ngày nhận việc", ""))

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

    next_row = len(sheet_cv_dau.col_values(2)) + 1
    sheet_cv_dau.update(f"A{next_row}:J{next_row}", [row])
    await update.message.reply_text("Đã lưu CV đậu.")


web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "HR Finn Bot is running"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)


def run_bot():
    telegram_app = ApplicationBuilder().token(TOKEN).build()
    telegram_app.add_handler(MessageHandler(filters.TEXT, handle))
    telegram_app.run_polling()


if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    run_bot()
