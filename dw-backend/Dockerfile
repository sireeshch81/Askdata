FROM askdata-ur-container

WORKDIR /app

ENV OPENAI_API_KEY="123456798"

COPY server_startup.sh .
COPY . .

RUN chmod +x server_startup.sh \
    && chown -R appuser:users /app

USER appuser

EXPOSE 5001

CMD ["/app/server_startup.sh"]
