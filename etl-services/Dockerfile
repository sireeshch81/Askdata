FROM askdata-ur-container

WORKDIR /app

RUN echo "alias ll='ls -lahF'" >> /home/appuser/.bashrc

COPY server_startup.sh .
COPY . .

RUN chmod +x run_all_etl_jobs.sh \
    && chmod +x server_startup.sh \
    && chown -R appuser:users /app \
    && chown appuser:users server_startup.sh \
    && chown appuser:users run_all_etl_jobs.sh

USER appuser

EXPOSE 5003

CMD ["/app/server_startup.sh"]
