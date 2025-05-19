# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app
COPY . .

# Expose port for Flask
EXPOSE 8080

# Set environment variables (will be overridden on Render)
ENV PORT=8080

# Start the app
CMD ["python", "bot.py"]
