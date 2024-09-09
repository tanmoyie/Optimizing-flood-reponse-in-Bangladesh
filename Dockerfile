FROM python:3.9-slim
RUN apt-get update && apt-get install -y git
COPY . /vrpctw_flood_app
WORKDIR /vrpctw_flood_app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN git clone https://github.com/tanmoyie/Optimizing-flood-reponse-in-Bangladesh.git
