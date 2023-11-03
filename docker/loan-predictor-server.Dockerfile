FROM python:3.11
WORKDIR /usr/loan-predictor-server
COPY requirement.txt .
RUN pip install --upgrade pip
RUN pip3 install  -r requirement.txt
COPY . .
CMD ["python",  "app.py"]