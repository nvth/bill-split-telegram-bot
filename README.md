# Split Bill Telegram Bot

Bot Telegram tao QR VietQR va chia bill theo so nguoi.

## Tinh nang
- Tao QR chuyen khoan tu STK va so tien
- Chia bill theo so nguoi, tinh moi nguoi bao nhieu
- Hien thi noi dung trong tin nhan (QR khong truyen noi dung)

## Yeu cau
- Python 3.11+
- Token Telegram bot

## Cau hinh
Tao file `.env`:
```
TELEGRAM_BOT_TOKEN=YOUR_TOKEN
```

Cap nhat ngan hang trong `data.txt`:
```
tpb, 970423, TPB
vcb, 970436, VCB
```
- Cot 1: key ngan hang (goi tren lenh)
- Cot 2: BIN
- Cot 3: ma ngan hang hien thi (tuy chon)

## Chay local
```
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python bot.py
```

## Chay bang Docker
```
docker build -t splitbill-bot .
docker run --env-file .env --restart unless-stopped splitbill-bot
```

## Docker Compose
```
docker compose up -d --build
```

## Lenh su dung
- `/b <bank> <stk> <sotien> [noidung]`
- `/s <bank> <stk> <sotien> <songuoi> [noidung]`
- `/help`

Vi du:
```
/b tpb 0123456789 50000 tien an
/s tpb 0123456789 210000 4 landcoffee
```
