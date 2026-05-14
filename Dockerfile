FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 2000

CMD ["gunicorn", "-b", "0.0.0.0:2000", "app:app"]