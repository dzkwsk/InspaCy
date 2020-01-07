FROM python:3.8

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install -r requirements.txt && python -m spacy download fr_core_news_md
ENV INSPACY_HOME=/usr/src/app
ENV FLASK_APP=/usr/src/app/inspacy/inspacy.py
ENV FLASK_ENV=production

COPY ./inspacy ./inspacy
RUN mkdir debug

CMD ["flask", "run", "--host=0.0.0.0"]
