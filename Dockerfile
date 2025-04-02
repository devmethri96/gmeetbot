# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy all application files
COPY . .  

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt  

# Expose the application port
EXPOSE 5000  

# Run the application
CMD ["python", "app.py"]

