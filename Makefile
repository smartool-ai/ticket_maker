lint:
	make black-lint
	make flake8-lint
	make mypy-lint

black-format:
	poetry run black .

black-lint:
	poetry run black . --check

flake8-lint:
	poetry run flake8

mypy-lint:
	poetry run mypy --no-namespace-packages .

build:
	sam build

build-docker:
	docker build -t latest -f Dockerfile.lambda .

deploy-docker-dev:
	docker push ${DEV_AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/rider:latest

deploy-docker-local:
	docker push ${LOCAL_AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/rider:latest

aws-login-dev:
	aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin ${DEV_AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com

aws-login-local:
	aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin ${LOCAL_AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com

sam-package-local:
	sam package \
		--region us-west-2 \
		--image-repository ${LOCAL_AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/rider \
		--s3-bucket jkbx-rider-builds-${STAGE_NAME} \
		--s3-prefix api_builds \
		--output-template-file packaged.yaml

sam-package-dev:
	sam package \
		--region us-west-2 \
		--image-repository ${DEV_AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/rider \
		--s3-bucket jkbx-rider-builds-${STAGE_NAME} \
		--s3-prefix api_builds \
		--output-template-file packaged.yaml

sam-package-staging:
	sam package \
		--region us-west-2 \
		--image-repository ${STAGING_AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/rider \
		--s3-bucket jkbx-rider-builds-${STAGE_NAME} \
		--s3-prefix api_builds \
		--output-template-file packaged.yaml

sam-package-staging-v2:
	sam package \
		--region us-west-2 \
		--image-repository ${STAGING_AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/rider-v2 \
		--s3-bucket jkbx-rider-builds-${STAGE_NAME} \
		--s3-prefix api_builds \
		--output-template-file packaged.yaml

sam-package-staging-v3:
	sam package \
		--region us-west-2 \
		--image-repository ${STAGING_AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/rider-v3 \
		--s3-bucket jkbx-rider-builds-${STAGE_NAME} \
		--s3-prefix api_builds \
		--output-template-file packaged.yaml

sam-package-production:
	sam package \
		--region us-west-2 \
		--image-repository ${PRODUCTION_AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/rider \
		--s3-bucket jkbx-rider-builds-${STAGE_NAME} \
		--s3-prefix api_builds \
		--output-template-file packaged.yaml

sam-package-demo:
	sam package \
		--region us-west-2 \
		--image-repository ${STAGING_AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/rider-demo \
		--s3-bucket jkbx-rider-builds-${STAGE_NAME} \
		--s3-prefix api_builds \
		--output-template-file packaged.yaml

sam-deploy-dev:
	make build
	make sam-package-dev

	sam deploy \
		--region us-west-2 \
		--image-repository ${DEV_AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/rider \
		--no-fail-on-empty-changeset \
		--template-file packaged.yaml \
		--stack-name RIDER-API-DEV \
		--capabilities CAPABILITY_IAM --parameter-overrides StageName=${STAGE_NAME} \
		JkbxConfiguration=${JKBX_CONFIGURATION} \
		AccountId=${DEV_AWS_ACCOUNT_ID} \
		Auth0Domain=${AUTH0_DOMAIN} \
		Auth0ClientId=${AUTH0_CLIENT_ID} \
		Auth0MgmtClientId=${AUTH0_MGMT_CLIENT_ID} \
		Auth0MgmtClientSecret=${AUTH0_MGMT_CLIENT_SECRET} \
		BrassicaServer=${BRASSICA_SERVER} \
		BrassicaToken=${BRASSICA_TOKEN}

sam-deploy-staging:
	make build
	make sam-package-staging

	sam deploy \
		--region us-west-2 \
		--image-repository ${STAGING_AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/rider \
		--no-fail-on-empty-changeset \
		--template-file packaged.yaml \
		--stack-name RIDER-API-STAGING \
		--capabilities CAPABILITY_IAM --parameter-overrides StageName=${STAGE_NAME} \
		JkbxConfiguration=${JKBX_CONFIGURATION} \
		AccountId=${STAGING_AWS_ACCOUNT_ID} \
		Auth0Domain=${AUTH0_DOMAIN} \
		Auth0ClientId=${AUTH0_CLIENT_ID} \
		Auth0MgmtClientId=${AUTH0_MGMT_CLIENT_ID} \
		Auth0MgmtClientSecret=${AUTH0_MGMT_CLIENT_SECRET} \
		BrassicaServer=${BRASSICA_SERVER} \
		BrassicaToken=${BRASSICA_TOKEN}

sam-deploy-local:
	make build
	make sam-package-local

	sam deploy \
		--region us-west-2 \
		--image-repository ${LOCAL_AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/rider \
		--no-fail-on-empty-changeset \
		--template-file packaged.yaml \
		--stack-name RIDER-API-LOCAL \
		--capabilities CAPABILITY_IAM --parameter-overrides StageName=${STAGE_NAME} \
		JkbxConfiguration=${JKBX_CONFIGURATION} \
		AccountId=${LOCAL_AWS_ACCOUNT_ID} \
		Auth0Domain=${AUTH0_DOMAIN} \
		Auth0ClientId=${AUTH0_CLIENT_ID} \
		Auth0MgmtClientId=${AUTH0_MGMT_CLIENT_ID} \
		Auth0MgmtClientSecret=${AUTH0_MGMT_CLIENT_SECRET} \
		BrassicaServer=${BRASSICA_SERVER} \
		BrassicaToken=${BRASSICA_TOKEN}

sam-deploy-production:
	make build
	make sam-package-production

	sam deploy \
		--region us-west-2 \
		--image-repository ${PRODUCTION_AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/rider \
		--no-fail-on-empty-changeset \
		--template-file packaged.yaml \
		--stack-name RIDER-API-PRODUCTION \
		--capabilities CAPABILITY_IAM --parameter-overrides StageName=${STAGE_NAME} \
		JkbxConfiguration=production \
		AccountId=${PRODUCTION_AWS_ACCOUNT_ID} \
		Auth0Domain=${AUTH0_DOMAIN_PRODUCTION} \
		Auth0ClientId=${AUTH0_CLIENT_ID_PRODUCTION} \
		Auth0MgmtClientId=${AUTH0_MGMT_CLIENT_ID_PRODUCTION} \
		Auth0MgmtClientSecret=${AUTH0_MGMT_CLIENT_SECRET_PRODUCTION} \
		BrassicaServer=${BRASSICA_SERVER} \
		BrassicaToken=${BRASSICA_TOKEN}

sam-serve:
	sam local start-api \
		--debug \
		-d 5858 \
		-p 5000 \
		--container-host localhost \
		--parameter-overrides \
		StageName=local \
		TranscriberConfiguration=${TRANSCRIBER_CONFIGURATION} \
		AccountId=${DEV_AWS_ACCOUNT_ID} \
		Auth0Domain=${AUTH0_DOMAIN} \
		Auth0ClientId=${AUTH0_CLIENT_ID}

cloud-test-app:
	sam sync --stack-name ${STACK_NAME} --watch
