#!/bin/bash
set -euo pipefail

# EB가 실행 중인 앱 컨테이너(이미지 기준) 하나 집기
CID=$(docker ps --filter "ancestor=aws_beanstalk/current-app" --format "{{.ID}}" | head -n 1)

if [ -z "${CID:-}" ]; then
  echo "[postdeploy] running app container not found"
  docker ps
  exit 1
fi

# Django 마이그레이션
docker exec "$CID" sh -lc 'python manage.py migrate --noinput'

# 정적 파일 수집이 필요하면 주석 해제
# docker exec "$CID" sh -lc 'python manage.py collectstatic --noinput'
