#!/bin/bash

sh "scripts/remove_postgres.sh"

docker volume create python-ai-experiments-postgres-data

docker run \
	-p 6024:5432 \
	--name python-ai-experiments-postgres \
	-e POSTGRES_PASSWORD=postgres \
	-e POSTGRES_USER=postgres \
	-e POSTGRES_DB=postgres \
	-v python-ai-experiments-postgres-data:/var/lib/postgresql/data \
	-d pgvector/pgvector:pg16
