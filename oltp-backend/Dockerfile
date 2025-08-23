FROM askdata-ur-container:latest

WORKDIR /app

COPY . .

COPY server_startup.sh .

RUN chown -R ${APPUSER}:users /app \
    && chmod +x /app/server_startup.sh \
    && echo "alias ll='ls -lahF'" >> /home/${APPUSER}/.bashrc \
    && echo "OLTP-BACKEND: Running in container" >> /home/${APPUSER}/hostinfo.txt

USER ${APPUSER}

EXPOSE 5002

CMD ["/app/server_startup.sh"]
