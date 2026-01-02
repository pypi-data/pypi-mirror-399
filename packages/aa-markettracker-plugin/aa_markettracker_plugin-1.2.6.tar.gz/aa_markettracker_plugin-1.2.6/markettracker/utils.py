import logging
import socket
import time
import uuid
import json

import requests
from celery import current_task
from django.conf import settings
from django.utils import timezone as _tz
from django.utils.dateparse import parse_datetime
from esi.errors import TokenInvalidError
from esi.models import Token
from eveuniverse.models import EveRegion
from requests.exceptions import HTTPError, RequestException

from allianceauth.groupmanagement.models import Group
from allianceauth.services.modules.discord.models import DiscordUser

from .models import (
    ContractSnapshot,
    MTTaskLog,
    TrackedContract,
    TrackedStructure,
    MarketTrackingConfig,
)


logger = logging.getLogger(__name__)
ESI_BASE_URL = "https://esi.evetech.net/latest"
HOSTNAME = socket.gethostname()

def _task_suffix(n: int = 8) -> str:
    tid = getattr(getattr(current_task, "request", None), "id", None) or uuid.uuid4().hex
    return str(tid).replace("-", "")[:n]

def esi_headers(access_token: str | None = None) -> dict:
    """
    Safe ESI headers builder.
    Never crashes if ESI_USER_AGENT is missing.
    """
    ua = (
        getattr(settings, "ESI_USER_AGENT", None)
        or getattr(settings, "ESI_USERAGENT", None)
        or "MarketTracker/1.0"
    )

    headers = {"User-Agent": ua}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    return headers


def esi_get_json(url: str, *, access_token: str | None, params: dict | None = None, timeout: int = 20,
                 source: str = "items", event: str = "esi_error", ctx: dict | None = None,
                 max_attempts: int = 4) -> tuple[list | dict | None, dict]:
    """
    GET to ESI with retry/backoff. Returns (json_data_or_none, meta).
    meta contains: status_code, headers, attempts, error
    """
    meta = {"status_code": None, "headers": {}, "attempts": 0, "error": None}

    backoff = 1.0
    for attempt in range(1, max_attempts + 1):
        meta["attempts"] = attempt
        try:
            resp = requests.get(
                url,
                headers=esi_headers(access_token),
                params=params or {},
                timeout=timeout,
            )
            meta["status_code"] = resp.status_code
            meta["headers"] = dict(resp.headers or {})

            # rate-limit / throttling
            if resp.status_code in (420, 429, 503):
                retry_after = resp.headers.get("Retry-After")
                reset = resp.headers.get("X-Esi-Error-Limit-Reset")
                wait_s = None
                if retry_after:
                    try:
                        wait_s = float(retry_after)
                    except ValueError:
                        pass
                if wait_s is None and reset:
                    try:
                        wait_s = float(reset)
                    except ValueError:
                        pass
                if wait_s is None:
                    wait_s = backoff

                # log only on the last attempt to avoid spamming
                if attempt == max_attempts:
                    db_log(
                        level="ERROR",
                        source=source,
                        event=event,
                        message=f"{resp.status_code} for {resp.url}",
                        data=_ctx({**(ctx or {}), "attempts": attempt, "wait_s": wait_s}),
                    )
                    return None, meta

                time.sleep(min(wait_s, 30.0))
                backoff = min(backoff * 2.0, 30.0)
                continue

            resp.raise_for_status()
            return (resp.json() or []), meta

        except (HTTPError, RequestException, ValueError) as e:
            meta["error"] = str(e)

            if attempt == max_attempts:
                db_log(
                    level="ERROR",
                    source=source,
                    event=event,
                    message=str(e),
                    data=_ctx({**(ctx or {}), "attempts": attempt}),
                )
                return None, meta

            time.sleep(min(backoff, 10.0))
            backoff = min(backoff * 2.0, 10.0)

    return None, meta


def _ctx(extra=None):
    data = {
        "host": HOSTNAME,
        "task_id": getattr(getattr(current_task, "request", None), "id", None),
    }
    if extra:
        data.update(extra)
    return data


def _location_name(config: MarketTrackingConfig) -> str:
    if not config:
        return "Unknown"
    if config.scope == "region":
        try:
            return EveRegion.objects.get(id=config.location_id).name
        except EveRegion.DoesNotExist:
            return str(config.location_id)
    else:
        try:
            return TrackedStructure.objects.get(structure_id=config.location_id).name
        except TrackedStructure.DoesNotExist:
            return str(config.location_id)
        
def _parse_esi_datetime(value):
    """
    Convert ESI ISO8601 datetime (with Z) into naive UTC datetime
    safe for MySQL DATETIME.
    """
    if not value:
        return None
    if isinstance(value, str):
        dt = parse_datetime(value)
        if dt:
            return dt.astimezone(_tz.utc).replace(tzinfo=None)
        return None
    if hasattr(value, "tzinfo"):
        return value.astimezone(_tz.utc).replace(tzinfo=None)
    return value

def resolve_ping_target(ping_value: str) -> str:
    if not ping_value:
        return ""
    if ping_value in ("@here", "@everyone"):
        return ping_value

    if ping_value.startswith("@"):
        group_name = ping_value[1:]
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            return f"@{group_name}"

        try:
            discord_group_info = DiscordUser.objects.group_to_role(group=group)
        except HTTPError:
            return f"@{group_name}"
        except Exception:
            return f"@{group_name}"

        if discord_group_info and "id" in discord_group_info:
            return f"<@&{discord_group_info['id']}>"
        return f"@{group_name}"

    return ""



def location_display(scope: str, location_id: int) -> str:
    """
    Location name.
    """
    if scope == "region":
        try:
            return EveRegion.objects.get(id=location_id).name
        except EveRegion.DoesNotExist:
            return str(location_id)
    else:
        try:
            return TrackedStructure.objects.get(structure_id=location_id).name
        except TrackedStructure.DoesNotExist:
            return str(location_id)


def resolve_ping_target_from_config(config) -> str:
    """
    Pings for discord messages
    """
    if config.discord_ping_group:
        try:
            mapping = DiscordUser.objects.group_to_role(group=config.discord_ping_group)
            role_id = mapping.get("id") if mapping else None
            if role_id:
                return f"<@&{role_id}>"
        except HTTPError:
            logger.exception("[MarketTracker] Discord service error when resolving group role")

        return f"@{config.discord_ping_group.name}"

    v = (config.discord_ping_group_text or "").strip()
    if v in {"here", "@here"}:
        return "@here"
    if v in {"everyone", "@everyone"}:
        return "@everyone"
    return ""


def contract_matches(tc: TrackedContract, snap: ContractSnapshot) -> tuple[bool, str]:
    """
    Checks whether a snapshot contract matches the tracked contract.
    Returns: (ok, reason)
    reason is always a short string (for diagnostics).
    """

    if not tc.is_active:
        return False, "inactive"

    # We only track item_exchange outstanding
    if (snap.type or "").lower() != "item_exchange":
        return False, "type_mismatch"

    if (snap.status or "").lower() != "outstanding":
        return False, "status_mismatch"

    # price gate (applies to both modes if max_price set)
    if tc.max_price and float(tc.max_price) > 0:
        price = float(snap.price or 0)
        if price > float(tc.max_price):
            logger.debug(
                "[match] snap %s price %.2f > max %.2f",
                snap.contract_id, price, float(tc.max_price),
            )
            return False, "price_too_high"

    title = (snap.title or "").strip()

    # ----- CUSTOM -----
    if tc.mode == TrackedContract.Mode.CUSTOM:
        filt = (tc.title_filter or "").strip()
        if not filt:
            return False, "no_title_filter"

        if filt.lower() not in title.lower():
            logger.debug(
                "[match] snap %s title '%s' !contains '%s'",
                snap.contract_id, title, filt,
            )
            return False, "title_mismatch"

        return True, "ok"

    # ----- DOCTRINE -----
    if tc.mode == TrackedContract.Mode.DOCTRINE:
        fit = tc.fitting
        if not fit or not getattr(fit, "ship_type_id", None):
            return False, "no_fitting"

        items = snap.items or []
        if isinstance(items, str):
            try:
                items = json.loads(items)
            except Exception:
                items = []
        if not isinstance(items, list):
            items = []
        if not items:
            logger.debug("[match] snap %s has no items json", snap.contract_id)
            return False, "no_items"

        ship_type_id = int(fit.ship_type_id)

        # count items in contract
        contract_counts: dict[int, int] = {}
        for it in items:
            try:
                t_id = int(it.get("type_id"))
                qty = int(it.get("quantity") or 0)
            except (TypeError, ValueError):
                continue
            contract_counts[t_id] = contract_counts.get(t_id, 0) + qty

        # must include the ship hull
        if contract_counts.get(ship_type_id, 0) < 1:
            logger.debug(
                "[match] snap %s missing ship type_id=%s",
                snap.contract_id, ship_type_id,
            )
            return False, "ship_missing"

        # build required modules list
        required_items: dict[int, int] = {}
        for slot in ("high_slots", "mid_slots", "low_slots", "rigs", "subsystems"):
            for mod in getattr(fit, slot, []) or []:
                try:
                    t_id = int(mod.type_id)
                except (TypeError, ValueError):
                    continue
                required_items[t_id] = required_items.get(t_id, 0) + 1

        # verify required modules exist
        for t_id, req_qty in required_items.items():
            have_qty = contract_counts.get(t_id, 0)
            if have_qty < req_qty:
                logger.debug(
                    "[match] snap %s missing module type_id=%s (have %s, need %s)",
                    snap.contract_id, t_id, have_qty, req_qty,
                )
                return False, "module_missing"

        return True, "ok"

    return False, "mode_unknown"




def fetch_contract_items(contract_obj, _access_token_unused, char_id):
    """
    Lazy item snapshot.
    Fetches items once per contract if missing.
    403 is normal (token not allowed to view that contract's items).
    """

    # already cached on snapshot
    if contract_obj.items:
        return contract_obj.items

    if not char_id:
        logger.warning(
            "[Contracts] Cannot fetch items for contract %s: missing owner char_id",
            contract_obj.contract_id,
        )
        return []

    tokens = Token.objects.filter(
        character_id=char_id,
        scopes__name="esi-contracts.read_character_contracts.v1",
    )

    if not tokens.exists():
        logger.warning(
            "[Contracts] No contracts token for character %s (contract %s)",
            char_id,
            contract_obj.contract_id,
        )
        return []

    url = f"{ESI_BASE_URL}/characters/{char_id}/contracts/{contract_obj.contract_id}/items/"

    for token in tokens:
        try:
            access_token = token.valid_access_token()
        except TokenInvalidError:
            logger.warning(
                "[Contracts] Invalid token for character %s (token id=%s)",
                char_id,
                token.id,
            )
            continue
        except Exception as e:
            logger.exception(
                "[Contracts] Token refresh failed for character %s (token id=%s): %s",
                char_id,
                token.id,
                e,
            )
            continue

        headers = {
            "User-Agent": getattr(settings, "ESI_USER_AGENT", "MarketTracker/1.0"),
            "Authorization": f"Bearer {access_token}",
        }

        try:
            resp = requests.get(url, headers=headers, timeout=10)

            # 403 = this char/token can't access items for that contract; not retryable
            if resp.status_code == 403:
                logger.info(
                    "[Contracts] Items not accessible for contract %s with char %s (403).",
                    contract_obj.contract_id,
                    char_id,
                )
                return []

            resp.raise_for_status()

            items = resp.json() or []
            contract_obj.items = items
            contract_obj.save(update_fields=["items"])

            db_log(source="contracts", event="items_saved", data={
                "contract_id": contract_obj.contract_id,
                "owner_character_id": char_id,
            })


            return items

        except Exception as e:
            logger.error(
                "[Contracts] Failed to load items for contract %s with char %s (token id=%s): %s",
                contract_obj.contract_id,
                char_id,
                token.id,
                e,
            )
            continue

    logger.warning(
        "[Contracts] Could not fetch items for contract %s (char %s) with any token",
        contract_obj.contract_id,
        char_id,
    )
    return []


def db_log(level="INFO", source="contracts", event="run", message="", data=None):
    try:
        MTTaskLog.objects.create(
            level=level,
            source=source,
            event=event,
            message=message,
            data=data or None,
        )
    except Exception:
        # logging must not crash the task
        pass
