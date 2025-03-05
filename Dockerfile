# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

#TO ADD PACKAGE
# Install required dependencies for msodbcsql18
# RUN apt-get update && apt-get install -y \
#     curl \
#     gnupg2 \
#     lsb-release \
#     ca-certificates \
#     sudo

# # Add Microsoft's GPG key and repository for msodbcsql18
# RUN curl https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc
# RUN curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | tee /etc/apt/sources.list.d/mssql-release.list

# # Update apt and install msodbcsql18
# RUN apt-get update && apt-get install -y msodbcsql18

RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    unixodbc \
    unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*
    
# Copy only requirements.txt first to leverage Docker's caching
COPY requirements.txt /app/

# Install dependencies (including Gunicorn)
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application files
COPY . /app/

# Expose the port Django runs on
EXPOSE 8000

# Run the application with Gunicorn
# CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn backend.wsgi:application --bind 0.0.0.0:8000"]


