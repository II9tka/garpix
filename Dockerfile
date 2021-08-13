FROM python:3.9.5

RUN mkdir -p static media/{videos,uploads}

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get upgrade -y && apt-get -y install postgresql gcc python3-dev musl-dev

RUN python3 -m pip install --upgrade pip
RUN pip install --no-cache-dir poetry

COPY pyproject.toml /app/
COPY poetry.lock /app/

RUN poetry config virtualenvs.create false

RUN poetry install

COPY . /app

RUN ["chmod", "+x" ,"/app/entrypoint.sh"]
ENTRYPOINT ["sh", "entrypoint.sh"]
