FROM python:2

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && apt-get update \
    && apt-get install nodejs -y

COPY . .

CMD [ "python", "./parse.py" ]