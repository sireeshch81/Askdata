FROM askdata-ur-container:latest

WORKDIR /app

COPY . .

USER appuser

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]

