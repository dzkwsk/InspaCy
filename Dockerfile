FROM python:3

WORKDIR /usr/src/app
USER root

COPY ./inspacy .
COPY requirements.txt ./

RUN pip install -r requirements.txt && python -m spacy download fr_core_news_md
ENV INSPACY_HOME=/usr/src/app
ENV FLASK_APP=/usr/src/app/inspacy/inspacy.py
ENV FLASK_ENV=production

CMD ["flask", "run"]