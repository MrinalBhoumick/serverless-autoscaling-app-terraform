# Use the official Python image with glibc
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app

# Expose the port that Streamlit uses
EXPOSE 8501

# Set the entrypoint to run Streamlit
CMD ["streamlit", "run", "app.py"]
