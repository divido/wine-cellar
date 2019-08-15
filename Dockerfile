FROM python:3.7-slim-buster

# Create a user to run the application and a place to put it
RUN useradd --create-home user
WORKDIR /home/user/wine-cellar

# Copy in all files, minus those in .dockerignore
COPY . ./

# Install as root
RUN pip install -r requirements.txt

# Decrease privleges and run
USER user
CMD [ "python", "inventory.py" ]
