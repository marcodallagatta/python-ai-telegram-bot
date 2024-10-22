FROM python:3.9-slim

WORKDIR /

# Create a virtual environment
ENV VIRTUAL_ENV=/venv
RUN python3 -m venv $VIRTUAL_ENV

# Update PATH to include the virtual environment's bin directory
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the application code
COPY . .

# Command to run the application
CMD ["python", "index.py"]
