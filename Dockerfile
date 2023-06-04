FROM python:3.11

WORKDIR /app

COPY requeirements.txt /app/

RUN pip install -r requeirements.txt

RUN pip install psycopg2-binary --force-reinstall --no-cache-dir

COPY . /app/

EXPOSE 8000