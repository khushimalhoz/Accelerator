VERSION ?= 1.0
CONF_PATH ?=${PWD}/config/aws_budget_config_sample.yml

build:
	docker build -t opstree/aws_budget_accelerator:$(VERSION) .
run:
	docker run -it --rm --name aws_budget_accelerator -v ${CONF_PATH}:/etc/ot/aws_budget_accelerator.yml:ro -e CONF_PATH='/etc/ot/aws_budget_accelerator.yml' -v ~/.aws:/root/.aws opstree/aws_budget_accelerator:${VERSION} 