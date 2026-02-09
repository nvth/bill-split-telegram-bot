import os
import shlex
import unicodedata
from pathlib import Path
from urllib.parse import urlencode, quote

from dotenv import load_dotenv

from telegram import BotCommand, Update
from telegram.ext import Application, CommandHandler, ContextTypes

DATA_FILE = Path(__file__).with_name("data.txt")
MARKDOWN_V2_SPECIAL = r"_*[]()~`>#+-=|{}.!"


def load_banks() -> dict:
    banks: dict[str, dict[str, str]] = {}
    if not DATA_FILE.exists():
        return banks
    for raw in DATA_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "," in line:
            parts = [p.strip() for p in line.split(",")]
        else:
            parts = shlex.split(line)
        if len(parts) < 2:
            continue
        key = parts[0].lower()
        bin_code = parts[1]
        bank_code = parts[2] if len(parts) >= 3 else key.upper()
        banks[key] = {
            "bin": bin_code,
            "code": bank_code,
        }
    return banks


def build_qr_url(bin_code: str, stk: str, amount: str, add_info: str | None = None) -> str:
    qr_base = f"https://img.vietqr.io/image/{bin_code}-{stk}-compact2.png"
    query = {"amount": amount}
    if add_info:
        query["addInfo"] = add_info
    return f"{qr_base}?{urlencode(query, quote_via=quote)}"


def parse_positive_int(value: str) -> int | None:
    try:
        parsed = int(value)
    except ValueError:
        return None
    return parsed if parsed > 0 else None


def parse_amount(value: str) -> int | None:
    raw = value.strip()
    if not raw:
        return None
    if raw[-1] in ("k", "K"):
        base_str = raw[:-1].replace(",", "").replace("_", "")
        base = parse_positive_int(base_str)
        return base * 1000 if base is not None else None
    cleaned = raw.replace(",", "").replace("_", "")
    return parse_positive_int(cleaned)


def escape_markdown_v2(text: str) -> str:
    escaped = []
    for ch in text:
        if ch in MARKDOWN_V2_SPECIAL:
            escaped.append(f"\\{ch}")
        else:
            escaped.append(ch)
    return "".join(escaped)


def normalize_qr_content(text: str, limit: int = 25) -> str:
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = []
    for ch in ascii_text.upper():
        if ch.isalnum() or ch in (" ", "-"):
            cleaned.append(ch)
    result = " ".join("".join(cleaned).split())
    return result[:limit].strip()


def escape_markdown(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("`", "'")
        .replace("*", "\\*")
        .replace("_", "\\_")
    )


async def cmd_c(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if len(args) < 1:
        await update.message.reply_text(
            "Dung lenh day du: \n"
            "/c [ma_ngan_hang] stk [so_tien] [so_nguoi] [noi_dung]\n"
            "Hoac ck cho em Hiep: \n"
            "/c [so_tien] [so_nguoi] [noi_dung]\n"
            "Mac dinh: khong can nhap so_nguoi neu so nguoi = 1"
        )
        return

    default_stk = os.getenv("DEFAULT_STK")
    default_bank = os.getenv("DEFAULT_BANK")

    if args[0].isalpha():
        if len(args) < 3:
            await update.message.reply_text(
                "Dung: /c ma_ngan_hang stk so_tien [so_nguoi] [noi_dung]"
            )
            return
        bank_key = args[0].lower()
        stk = args[1]
        amount_raw = args[2]
        idx = 3
    else:
        bank_key = default_bank
        stk = default_stk
        amount_raw = args[0]
        idx = 1

    people = None
    if len(args) > idx:
        maybe_people = parse_positive_int(args[idx])
        if maybe_people is not None:
            people = maybe_people
            idx += 1
    if people is None:
        people = 1

    content = " ".join(args[idx:]).strip() if len(args) > idx else ""

    amount_total = parse_amount(amount_raw)
    if amount_total is None or people is None:
        await update.message.reply_text(
            "So tien va so nguoi phai la so nguyen duong."
        )
        return

    banks = load_banks()
    if bank_key not in banks:
        await update.message.reply_text(
            f"Khong tim thay ngan hang: {bank_key}. "
            "Kiem tra data.txt."
        )
        return

    bank_info = banks[bank_key]
    bin_code = bank_info["bin"]
    bank_code = bank_info["code"]
    content_text = content if content else ""

    amount_each = amount_total // people
    qr_add_info = normalize_qr_content(content_text)
    qr_url = build_qr_url(
        bin_code,
        stk,
        str(amount_each),
        qr_add_info if qr_add_info else None,
    )

    content_display = escape_markdown(content_text if content_text else "(khong co)")
    message = (
        "Thong tin chia bill:\n"
        f"Bank: {escape_markdown(bank_code)}\n"
        f"STK: `{escape_markdown(stk)}`\n"
        f"So tien: {amount_total}\n"
        f"So nguoi: {people}\n"
        f"Moi nguoi: `{amount_each}`\n"
        f"Noi dung: {content_display}"
    )

    try:
        await update.message.reply_photo(
            qr_url,
            caption=message,
            parse_mode="Markdown",
        )
    except Exception:
        await update.message.reply_text(message, parse_mode="Markdown")
        await update.message.reply_text(
            "Khong gui duoc anh QR. Vui long thu lai."
        )
        return
    try:
        if update.message:
            await update.message.delete()
    except Exception:
        pass


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/c chia bill\n"
        "============\n"
        "Dung day du: \n"
        "/c [ma_ngan_hang] [stk] [so_tien] [so_nguoi] [noi_dung](optional)\n"
        "Hoac: \n"
        "/c [ma_ngan_hang] [stk] [so_tien] [noi_dung](optional) (mac dinh so nguoi = 1)\n"
        "============\n"
        "Mac dinh chuyen khoan cho em Hiep:\n"
        "/c [so_tien] [so_nguoi] [noi_dung](optional)\n"
        "============\n"
        "Luu y: Khong can nhap so nguoi neu so nguoi = 1"
    )


async def post_init(app: Application) -> None:
    await app.bot.set_my_commands(
        [
            BotCommand("c", "Chia bill: /c ..."),
            BotCommand("help", "Huong dan su dung"),
        ]
    )


def main() -> None:
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("Missing TELEGRAM_BOT_TOKEN env var")

    print("Bot is starting")
    app = Application.builder().token(token).post_init(post_init).build()
    app.add_handler(CommandHandler("c", cmd_c))
    app.add_handler(CommandHandler("help", cmd_help))
    print("Bot is started")
    app.run_polling()


if __name__ == "__main__":
    main()
