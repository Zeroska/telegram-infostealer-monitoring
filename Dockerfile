FROM python:3.11
WORKDIR /telegram-monitoring
ADD src src
ADD requirements.txt . 
ADD .env .
RUN pip3 install -r requirements.txt
CMD ["python", "src/main.py"]

