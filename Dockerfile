FROM python:3.8

WORKDIR /home

ENV TELEGRAM_API_TOKEN=""
ENV GITHUB_API_TOKEN=""

COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]