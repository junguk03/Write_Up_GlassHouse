FROM python:3.12-slim

WORKDIR /srv

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 180 --retries 10 -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh \
    && mkdir -p uploads archive internal \
    && useradd --create-home app \
    && chown -R app:app /srv

USER app

EXPOSE 8005

ENTRYPOINT ["./entrypoint.sh"]
