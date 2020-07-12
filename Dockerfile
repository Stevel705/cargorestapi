FROM python:3
ADD app/ /app 
WORKDIR /app
RUN apt update 
RUN pip install -r requirements.txt

CMD python create_db.py
ENTRYPOINT python app.py