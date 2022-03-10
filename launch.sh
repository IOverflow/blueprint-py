#! /bin/ash

if [[ -z "${SECRET_JWT_KEY_FILE}" ]]; then
  exit 1
else
  export SECRET_JWT_KEY="$(cat "$SECRET_JWT_KEY_FILE")"
fi


if [[ -z "${SECRET_REFRESH_JWT_KEY_FILE}" ]]; then
  exit 1
else
  export SECRET_REFRESH_JWT_KEY="$(cat "$SECRET_REFRESH_JWT_KEY_FILE")"
fi

if [[ -z "${DEVELOPMENT_DATABASE_URL_FILE}" ]]; then
  exit 1
else
  export DEVELOPMENT_DATABASE_URL="$(cat "$DEVELOPMENT_DATABASE_URL_FILE")"
fi

if [[ -z "${DEVELOPMENT_DATABASE_FILE}" ]]; then
  exit 1
else
  export DEVELOPMENT_DATABASE="$(cat "$DEVELOPMENT_DATABASE_FILE")"
fi

# Launch server
uvicorn src.main:api --host 0.0.0.0 --port 8000