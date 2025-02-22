FROM python:3.11

# Install build tools and ALSA development headers
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libpq-dev \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements.txt first to leverage Docker cache
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

EXPOSE 8000

CMD ["sh", "./bin/start.sh"]
