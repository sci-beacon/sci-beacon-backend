FROM python:3.11.9-alpine

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade pip wheel

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

ENV PYTHONUNBUFFERED=1

# CMD ["uvicorn", "questionbank_launch:app", "--host", "0.0.0.0", "--port", "5501", "--env-file", "dev.env"]
