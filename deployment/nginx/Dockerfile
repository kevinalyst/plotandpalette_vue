# Nginx Reverse Proxy Dockerfile
# Plot & Palette - Frontend Server & API Gateway
FROM nginx:1.25-alpine

# Install curl for health checks
RUN apk add --no-cache curl

# Remove default nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf
COPY site.conf /etc/nginx/conf.d/site.conf

# Create directories for static assets
RUN mkdir -p /usr/share/nginx/html/assets/images \
             /usr/share/nginx/html/assets/emotions \
             /usr/share/nginx/html/assets/palettes \
             /usr/share/nginx/html/uploads

# Set proper permissions
RUN chown -R nginx:nginx /usr/share/nginx/html

# Expose ports
EXPOSE 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 