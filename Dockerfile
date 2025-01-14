FROM python:slim-buster AS builder

ENV CONF_PATH=/etc/ot/budget.yml

WORKDIR /opt/

COPY . .

RUN apt-get update && \
    apt-get install -y binutils libc-bin git

RUN pip3 install --no-cache --upgrade -r requirements.txt

RUN pyinstaller --paths=lib scripts/aws_budget_factory.py --onefile


# FROM opstree/python3-distroless:1.0 . (It supports only AMD now .. will work on it)

RUN cp dist/aws_budget_factory .

ENTRYPOINT ["./aws_budget_factory"]
