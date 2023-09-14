FROM --platform=linux/amd64 python:3.10-bullseye

WORKDIR /pieval

RUN apt-get update && apt-get install -y --no-install-recommends net-tools unixodbc-dev python3-dev

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

# Itentionally not copying code into image
# code will be mounted in the run command instead
# CMD [ "gunicorn", "-w 4", "-b 0.0.0.0:5001", "run:create_app()" ]