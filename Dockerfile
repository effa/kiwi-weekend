FROM benkalukas/py_weekend_base

WORKDIR /app

COPY Pipfile* /app/

RUN pipenv install --system --deploy

COPY . /app

CMD ["gunicorn", "api:app", "--bind=0.0.0.0:8000"]
