# Use official Python image
FROM python:3.9-slim

# Set workdir
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt requirements.txt

# Install dependencies
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt


# Copy app code
COPY app.py app.py

# Expose Streamlit port
EXPOSE 8051

# Run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8051", "--server.address=0.0.0.0"]
