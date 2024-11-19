FROM joyzoursky/python-chromedriver:3.9

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

CMD fastapi run --reload