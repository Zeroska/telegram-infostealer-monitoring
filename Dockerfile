FROM python:3.11
ADD src . 
RUN pip3 install -r requirement.txt
CMD ["python", ".src/main.py"]
