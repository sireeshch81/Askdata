FROM askdata-ur-container:latest

WORKDIR /app


COPY src/ ./src/
COPY config/ ./config/

RUN mkdir -p output

ENV PYTHONPATH=/app

CMD ["python3", "src/main.py", "--help"]
