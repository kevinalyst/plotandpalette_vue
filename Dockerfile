# Use official Node.js runtime as the base image
FROM node:18-alpine

# Set the working directory
WORKDIR /app

# Install Python and required system dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    python3-dev \
    gcc \
    g++ \
    musl-dev \
    linux-headers \
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    curl

# Create Python requirements file for recommendation system and story generation
RUN printf 'pandas>=2.0.0\nnumpy>=1.24.0\nscikit-learn>=1.3.0\nPillow>=10.0.0\njoblib>=1.3.0\nrequests>=2.31.0\nanthropic>=0.3.0\npython-dotenv>=0.19.0\n' > python-requirements.txt

# Install Python dependencies (using --break-system-packages for Alpine)
RUN pip3 install --no-cache-dir --break-system-packages -r python-requirements.txt

# Copy package files
COPY package*.json ./

# Install Node.js dependencies
RUN npm install --only=production

# Copy the rest of the application code
COPY . .

# Create uploads directory and set permissions
RUN mkdir -p uploads && \
    chmod 755 uploads

# Copy recommendation data files to accessible location
RUN mkdir -p /app/recommendation_data && \
    cp Recommandations/*.csv /app/recommendation_data/ 2>/dev/null || true && \
    cp Recommandations/*.py /app/recommendation_data/ 2>/dev/null || true

# Expose the port
EXPOSE 3000

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

# Start the application
CMD ["npm", "start"] 