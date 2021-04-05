FROM python:3.8

WORKDIR /Movieholic-app

COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8000

COPY ./Movieholic-app ./Movieholic-app

CMD ["python", "./Movieholic-app/__init__.py"]
