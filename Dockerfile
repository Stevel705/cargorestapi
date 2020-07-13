FROM python:3
ADD app/ /app 
WORKDIR /app
RUN apt update 
RUN pip install -r requirements.txt

RUN python create_db.py
CMD python app.py