# Start from the official Python base image.
FROM python:3.9-alpine

# Set the current working directory to /code.
#
# This is where we'll put the requirements.txt file and the app directory.
WORKDIR /code

# Copy the file with the requirements to the /code directory.
#
# Copy only the file with the requirements first, not the rest of the code.
#
# As this file doesn't change often, Docker will detect it and use the cache for this step, enabling the cache for the next step too.
COPY ./requirements.txt /code/requirements.txt


# Install the package dependencies in the requirements file.
#
# The --no-cache-dir option tells pip to not save the downloaded packages locally,
# as that is only if pip was going to be run again to install the same packages,
# but that's not the case when working with containers.

RUN apk add --update --no-cache --virtual .tmp-build-deps gcc libc-dev linux-headers libffi-dev make
RUN pip3 install --upgrade pip && pip3 install -r /code/requirements.txt

RUN apk del .tmp-build-deps


#
COPY ./src /code/src
RUN rm -f /code/src/.env
COPY ./launch.sh /code/launch.sh
RUN chmod +x launch.sh
RUN ls /code
# Set the command to run the uvicorn server.
#
# CMD takes a list of strings, each of these strings is what you would type in the command line separated by spaces.
#
# This command will be run from the current working directory, the same /code directory you set above with WORKDIR /code.
#
# Because the program will be started at /code and inside of it is the directory ./app with your code, Uvicorn will be able
# to see and import app from app.main.
ENTRYPOINT ["./launch.sh"]