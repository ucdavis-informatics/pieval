FROM python:3.8.6-buster

WORKDIR /pieval

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
   && apt-get -y install --no-install-recommends unixodbc-dev python3-dev \
    #
    # Install ms sql server driver
   && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
   && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
   && apt-get -y update \
   && ACCEPT_EULA=Y apt-get -y install msodbcsql17 \
    # Clean up
   && apt-get autoremove -y \
   && apt-get clean -y \
   && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install net-tools

ENV DEBIAN_FRONTEND=dialog

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

# Itentionally not copying code into image
# code will be mounted in the run command instead

# CMD [ "gunicorn", "-w 4", "-b 0.0.0.0:5001", "run:create_app()" ]