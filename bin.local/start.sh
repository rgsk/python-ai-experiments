sh scripts/restart_postgres.sh

sed -i '' 's/localhost/host.docker.internal/g' .env


docker run -d \
-p 8000:8000 \
--env-file .env \
--name python-ai-experiments \
rgskartner/python-ai-experiments

sed -i '' 's/host.docker.internal/localhost/g' .env