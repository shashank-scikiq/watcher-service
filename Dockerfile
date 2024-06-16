FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app/

COPY entry.sh /app/entry.sh
RUN chmod +x /app/entry.sh

EXPOSE 8080

ENTRYPOINT ["/app/entry.sh"]

CMD ["python", "/app/watcher.py"]

