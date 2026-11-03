FROM python:3.12-slim-bookworm

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /srv

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 180 --retries 10 -r requirements.txt
RUN playwright install --with-deps chromium \
    && chmod -R a+rX /ms-playwright

COPY bot.py .

RUN useradd --create-home bot && chown -R bot:bot /srv
USER bot

EXPOSE 5000

CMD ["python", "bot.py"]
