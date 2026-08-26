# Frontend Dockerfile - Minimal Chatbot-Only UI
# Single stage - just nginx serving standalone HTML
FROM nginx:alpine

# Copy nginx configuration for chatbot-only setup
RUN echo 'server { \
    listen 80; \
    server_name _; \
    root /usr/share/nginx/html; \
    index chatbot-only.html; \
    client_max_body_size 50M; \
    \
    location / { \
        try_files $uri $uri/ /chatbot-only.html; \
        add_header Cache-Control "no-cache, must-revalidate"; \
    } \
    \
    location = /health { \
        access_log off; \
        return 200 "healthy\n"; \
        add_header Content-Type text/plain; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Copy the chatbot-only HTML file
COPY chatbot-only.html /usr/share/nginx/html/

# Optional: Copy assets if any
COPY public/ /usr/share/nginx/html/ 2>/dev/null || true

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
