
FROM python:3.8-slim

WORKDIR /app
COPY requirements.txt /app
RUN pip install --trusted-host pypi.python.org -r requirements.txt
COPY . /app
EXPOSE 8080

ENV FLASK_APP=backend/app.py
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
