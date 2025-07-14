# Use official Node.js runtime as the base image
FROM node:18-alpine

# Set the working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the port
EXPOSE 8080

# Set environment to production
ENV NODE_ENV=production

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Install curl for health check
RUN apk add --no-cache curl

# Start the development server (for production, you'd use npm run build and serve static files)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"] 