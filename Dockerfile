FROM python:3.9.7-slim
WORKDIR /app
COPY requirement.txt requirement.txt
RUN pip3 install -r requirement.txt
COPY main.py main.py
CMD ["python3", "main.py"]
