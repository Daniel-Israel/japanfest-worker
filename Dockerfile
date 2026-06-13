FROM python:3.13-slim-trixie

COPY requirements.txt /requirements.txt

RUN python3.13 -m pip install --no-cache-dir -r /requirements.txt

COPY start.sh /start.sh

RUN chmod -x /start.sh

COPY worker /worker

CMD ["sh", "/start.sh"]