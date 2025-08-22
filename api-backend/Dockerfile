FROM askdata-ur-container

WORKDIR /app

COPY pyproject.toml .
COPY .env .
COPY server_startup.sh .
COPY . .

ENV GEMINI_API_KEY="AIzaSyBXdG0nUWgFhrCKOewbUr34RM7_wBz0OCQ"

COPY --from=builder /app/venv /app/venv/

RUN chmod +x server_startup.sh \
    && chown -R appuser:appuser /app \
    && chown appuser:appuser server_startup.sh

USER appuser

EXPOSE 5004

CMD ["/app/server_startup.sh"]
