FROM python:3.10

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python data_ingest.py

EXPOSE 7860
CMD ["streamlit","run","streamlit_app.py","--server.port=7860","--server.address=0.0.0.0"]
