FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1
ENV APP_DIR .
ENV PYTHONPATH "${PYTHONPATH}:${APP_DIR}"
WORKDIR $APP_DIR

RUN pip install --upgrade pip

COPY requirements.txt $APP_DIR/
RUN pip install -r requirements.txt

COPY settings.py $APP_DIR/

CMD ["gunicorn", "-c", "settings.py", "api.main:app"]
