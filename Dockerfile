FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements /code/requirements
RUN pip install --no-cache -r requirements/production.txt
COPY . /code/
