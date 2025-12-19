#!/bin/bash
set -euo pipefail

PROJECT_ID="colour-emotion-project"
REGION="europe-west2"
SERVICE="plot-and-palette"

echo "Creating secrets (idempotent)..."
echo -n "${DB_PASSWORD:-Lihanwen1997}" | gcloud secrets create db-password --data-file=- --replication-policy=automatic --project ${PROJECT_ID} || true
echo -n "${OPENAI_API_KEY:-}" | gcloud secrets create openai-api-key --data-file=- --replication-policy=automatic --project ${PROJECT_ID} || true

echo "Granting service account access to secrets..."
SA="${PROJECT_ID}@appspot.gserviceaccount.com"
gcloud secrets add-iam-policy-binding db-password --member=serviceAccount:${SA} --role=roles/secretmanager.secretAccessor --project ${PROJECT_ID} || true
gcloud secrets add-iam-policy-binding openai-api-key --member=serviceAccount:${SA} --role=roles/secretmanager.secretAccessor --project ${PROJECT_ID} || true

echo "Deploying Cloud Run service from service.cloudrun.yaml..."
gcloud run services replace service.cloudrun.yaml \
  --region ${REGION} \
  --project ${PROJECT_ID}

echo "Allowing unauthenticated access..."
gcloud run services add-iam-policy-binding ${SERVICE} \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --region ${REGION} \
  --project ${PROJECT_ID} || true

echo "Done. Retrieve URL:"
gcloud run services describe ${SERVICE} --region ${REGION} --project ${PROJECT_ID} --format='value(status.url)'


