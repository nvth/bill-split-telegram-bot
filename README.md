# Split Bill Telegram Bot

Bot Telegram tao QR VietQR va chia bill theo so nguoi.

## Tinh nang
- Tao QR chuyen khoan theo ngan hang va so tien
- Chia bill theo so nguoi, tinh moi nguoi bao nhieu
- Ho tro nhap so tien dang 50k = 50000

## Yeu cau
- Python 3.11+
- Token Telegram bot

## Cau hinh
Tao file `.env`:
```
TELEGRAM_BOT_TOKEN=YOUR_TOKEN
DEFAULT_BANK=tpb
DEFAULT_STK=xxxxx
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
Chi co mot lenh `/c`.

### Dang day du (tu chon ngan hang)
```
/c ma_ngan_hang stk so_tien so_nguoi noi_dung
```
Neu so nguoi = 1, co the bo qua:
```
/c ma_ngan_hang stk so_tien noi_dung
```

### Dang mac dinh cho Hiep
Mac dinh lay tu `.env`: `DEFAULT_BANK` va `DEFAULT_STK`.
```
/c so_tien so_nguoi noi_dung
```
Neu so nguoi = 1, co the bo qua:
```
/c so_tien noi_dung
```

### Vi du
```
/c tpb 0123456789 210000 4 landcoffee
/c tpb 0123456789 50k tien an
/c 50k 3 tien an
/c 50k
```
