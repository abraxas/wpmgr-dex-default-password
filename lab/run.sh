#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
HERE="$(pwd)"
PIN_COMMIT="e1b3a163988c9f1c31bc93922ea34322fa188792"
REPO_URL="${WPMGR_SRC_URL:-https://github.com/mosamlife/wpmgr.git}"
PIN="${HERE}/src"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-wpmgrh18}"
export PYTHONUNBUFFERED=1
export WPMGR_PIN="${PIN}"

LABEL="WPMGR-H18-DEX-DEFAULT"
WITNESS="WPMGR-H18-DEX-CREATED-TENANT"
IMAGE="wpmgr-lab:v0.61.199"

WEB_HOST_PORT=18210
API_HOST_PORT=18211
PG_HOST_PORT=18212
REDIS_HOST_PORT=18213
DEX_HOST_PORT=18214

down() {
  docker compose -p "${COMPOSE_PROJECT_NAME}" down -v --remove-orphans >/dev/null 2>&1 || true
}

fail_setup() {
  local reason="$1"
  echo "FAIL ${LABEL} ${reason} ${WITNESS}" | tee poc-last-run.txt
  down
  exit 1
}

port_free() {
  local p="$1"
  ! lsof -nP -iTCP:"${p}" -sTCP:LISTEN >/dev/null 2>&1
}

pick_ports() {
  if port_free 18210 && port_free 18211 && port_free 18212 && port_free 18213 && port_free 18214; then
    return 0
  fi
  local found=()
  local p
  for p in $(seq 18360 18380); do
    if port_free "${p}"; then
      found+=("${p}")
    fi
  done
  if [[ "${#found[@]}" -lt 5 ]]; then
    fail_setup "ports-busy"
  fi
  WEB_HOST_PORT="${found[0]}"
  API_HOST_PORT="${found[1]}"
  PG_HOST_PORT="${found[2]}"
  REDIS_HOST_PORT="${found[3]}"
  DEX_HOST_PORT="${found[4]}"
}

write_dex_config() {
  sed -e "s#http://127.0.0.1:[0-9][0-9]*/auth/oidc/callback#http://127.0.0.1:${WEB_HOST_PORT}/auth/oidc/callback#" \
    "${HERE}/dex-config.yaml" >"${HERE}/dex-config.yaml.tmp"
  mv "${HERE}/dex-config.yaml.tmp" "${HERE}/dex-config.yaml"
}

ensure_image() {
  if docker image inspect "${IMAGE}" >/dev/null 2>&1; then
    echo "IOC image-present ${IMAGE}"
    return 0
  fi
  echo "== flock build ${IMAGE} =="
  exec 9>/tmp/wpmgr-lab-image.lock
  flock 9
  if docker image inspect "${IMAGE}" >/dev/null 2>&1; then
    echo "IOC image-present-after-lock ${IMAGE}"
    flock -u 9
    return 0
  fi
  local arch
  arch="$(uname -m)"
  case "${arch}" in
    x86_64) arch=amd64 ;;
    aarch64 | arm64) arch=arm64 ;;
  esac
  if ! docker build \
    --file "${HERE}/Dockerfile" \
    --tag "${IMAGE}" \
    --build-arg VERSION=0.61.199 \
    --build-arg TARGETOS=linux \
    --build-arg TARGETARCH="${arch}" \
    "${PIN}"; then
    flock -u 9
    fail_setup "image-build-failed"
  fi
  flock -u 9
}

up_with_retry() {
  local attempt
  for attempt in 1 2 3 4 5 6; do
    echo "== docker compose up attempt=${attempt} =="
    if docker compose -p "${COMPOSE_PROJECT_NAME}" up -d; then
      return 0
    fi
    echo "IOC compose-up-retry attempt=${attempt}"
    docker compose -p "${COMPOSE_PROJECT_NAME}" down -v --remove-orphans >/dev/null 2>&1 || true
    sleep $((attempt * 8))
  done
  return 1
}

wait_url() {
  local url="$1"
  local header="${2:-}"
  local i code
  for i in $(seq 1 90); do
    if [[ -n "${header}" ]]; then
      code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 -H "${header}" "${url}" || true)"
    else
      code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 "${url}" || true)"
    fi
    if [[ "${code}" == "200" ]]; then
      echo "IOC ready ${url} attempt=${i} http=${code}"
      return 0
    fi
    echo "IOC wait ${url} attempt=${i} http=${code}"
    sleep 2
  done
  return 1
}

trap down EXIT

ensure_pin() {
  if [[ ! -e "${PIN}/.git" ]]; then
    git clone --filter=blob:none --no-checkout "${REPO_URL}" "${PIN}" || fail_setup "clone-failed"
    git -C "${PIN}" fetch --depth 1 origin "${PIN_COMMIT}" || fail_setup "fetch-failed"
    git -C "${PIN}" checkout --detach FETCH_HEAD || fail_setup "checkout-failed"
  fi
  local got
  got="$(git -C "${PIN}" rev-parse HEAD)"
  if [[ "${got}" != "${PIN_COMMIT}" ]]; then
    fail_setup "pin-mismatch"
  fi
}

ensure_pin
if [[ ! -f "${PIN}/infra/docker-compose.yml" || ! -f "${PIN}/infra/dex/config.yaml" ]]; then
  fail_setup "pin-missing"
fi

pick_ports
write_dex_config
export WEB_HOST_PORT API_HOST_PORT PG_HOST_PORT REDIS_HOST_PORT DEX_HOST_PORT
export WPMGR_H18_WEB_PORT="${WEB_HOST_PORT}"
export WPMGR_H18_API_PORT="${API_HOST_PORT}"
export WPMGR_H18_DEX_PORT="${DEX_HOST_PORT}"

echo "IOC ports web=${WEB_HOST_PORT} api=${API_HOST_PORT} pg=${PG_HOST_PORT} redis=${REDIS_HOST_PORT} dex=${DEX_HOST_PORT}"

if grep -E '^\s+-\s+"[^"]+:[0-9]+"' docker-compose.yml | grep -v '127.0.0.1'; then
  fail_setup "lab-compose-not-loopback"
fi

down
ensure_image

if ! up_with_retry; then
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=80 || true
  fail_setup "compose-up-failed"
fi

if ! wait_url "http://127.0.0.1:${DEX_HOST_PORT}/dex/.well-known/openid-configuration" "Host: dex:5556"; then
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=80 dex || true
  fail_setup "dex-not-ready"
fi

if ! wait_url "http://127.0.0.1:${API_HOST_PORT}/readyz"; then
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=120 api || true
  fail_setup "api-not-ready"
fi

if ! wait_url "http://127.0.0.1:${WEB_HOST_PORT}/"; then
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=40 web || true
  fail_setup "web-not-ready"
fi

echo "== poc.py =="
set +e
python3 ./poc.py
rc=$?
set -e

if [[ ! -f poc-last-run.txt ]] || ! tail -n 1 poc-last-run.txt | grep -qE '^(SUCCESS|FAIL) '; then
  echo "FAIL ${LABEL} poc-exit-${rc} ${WITNESS}" >> poc-last-run.txt
  rc=1
fi

exit "${rc}"
