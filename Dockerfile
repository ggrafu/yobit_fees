FROM python:2

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && sudo apt-get update \
    && sudo apt-get install nodejs

COPY . .

CMD [ "python", "./parse.py" ]