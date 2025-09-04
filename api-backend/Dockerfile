FROM askdata-ur-container:latest

WORKDIR /app

COPY server_startup.sh .
COPY . .

# Install MySQL driver
USER root
RUN pip install --no-cache-dir mysql-connector-python

ENV GEMINI_API_KEY="AIzaSyBXdG0nUWgFhrCKOewbUr34RM7_wBz0OCQ"

RUN chmod +x server_startup.sh \
    && chown -R appuser:users /app

USER appuser

EXPOSE 5004

CMD ["/app/server_startup.sh"]
