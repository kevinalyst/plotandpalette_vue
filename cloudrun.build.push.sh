#!/bin/bash
set -euo pipefail

PROJECT_ID="colour-emotion-project"
REGION="europe-west2"
REPO="p-and-p-containers"
AR="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}"

echo "Enabling services..."
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com --project ${PROJECT_ID}

echo "Configuring docker auth..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

SHA=$(git rev-parse --short HEAD || date +%s)

echo "Ensuring buildx builder..."
docker buildx ls >/dev/null 2>&1 || docker buildx create --use --name ppbuilder
docker buildx use ppbuilder || true

echo "Building images for linux/amd64 and pushing..."
docker buildx build --platform=linux/amd64 -t ${AR}/backend:${SHA} -f Dockerfile . --push
docker buildx build --platform=linux/amd64 -t ${AR}/story-api:${SHA} -f story_generation/Dockerfile story_generation --push
docker buildx build --platform=linux/amd64 -t ${AR}/nginx-cloudrun:${SHA} -f deployment/nginx/Dockerfile.cloudrun . --push

echo "Tagging latest and promoting..."
docker buildx imagetools create -t ${AR}/backend:latest ${AR}/backend:${SHA}
docker buildx imagetools create -t ${AR}/story-api:latest ${AR}/story-api:${SHA}
docker buildx imagetools create -t ${AR}/nginx-cloudrun:latest ${AR}/nginx-cloudrun:${SHA}

echo "All images built and pushed."


