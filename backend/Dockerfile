# Enter your code below 
# Use Python 3.11 Alpine 3.18 as base image
FROM python:3.11-alpine3.18

# Set the working directory in the container
WORKDIR /usr/app

# Copy the requirements file and install Python dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . .

# Expose port 5000 to access the application
EXPOSE 5000

# Set the command to run the application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]

