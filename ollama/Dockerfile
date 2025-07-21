FROM ollama/ollama:latest

# Expose the Ollama server port
EXPOSE 11434

# Copy the startup script into the container
COPY startup.sh /startup.sh
RUN chmod +x /startup.sh

# Use the startup script as the entrypoint
ENTRYPOINT ["/startup.sh"]
