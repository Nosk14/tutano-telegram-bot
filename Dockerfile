FROM python:3.8-slim
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY tutano-telegram-bot /usr/local/bot/
CMD python3 /usr/local/bot/bot.py