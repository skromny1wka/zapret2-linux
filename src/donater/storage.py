from __future__ import annotations

import hashlib
import platform
import time
from datetime import datetime
from typing import Any, Dict, Optional

from settings import store as settings_store


class PremiumStorage:
    """Хранилище Premium-состояния в общем settings.json."""

    @staticmethod
    def _machine_info() -> str:
        try:
            return f"{platform.machine()}-{platform.processor()}-{platform.node()}"
        except Exception:
            return "unknown"

    @staticmethod
    def _cache_payload(*, signed_payload: Dict[str, Any], kid: Optional[str], sig: Optional[str]) -> dict[str, Any]:
        return {
            "kid": kid,
            "sig": sig,
            "signed": signed_payload,
            "cached_at": int(time.time()),
        }

    @staticmethod
    def get_device_id() -> str:
        device_id = (settings_store.get_premium_device_id() or "").strip()
        if device_id:
            return device_id

        device_id = hashlib.md5(PremiumStorage._machine_info().encode()).hexdigest()
        settings_store.set_premium_device_id(device_id)
        return device_id

    @staticmethod
    def get_device_token() -> Optional[str]:
        return settings_store.get_premium_device_token()

    @staticmethod
    def set_device_token(token: str) -> bool:
        token = (token or "").strip()
        if not token:
            return False
        return bool(settings_store.set_premium_device_token(token))

    @staticmethod
    def clear_device_token() -> bool:
        return bool(settings_store.set_premium_device_token(None))

    @staticmethod
    def get_last_check() -> Optional[datetime]:
        raw = settings_store.get_premium_last_check()
        if not raw:
            return None
        try:
            return datetime.fromisoformat(raw)
        except Exception:
            return None

    @staticmethod
    def save_last_check() -> bool:
        return bool(settings_store.set_premium_last_check(datetime.now().isoformat()))

    @staticmethod
    def get_last_network_failure_ts() -> Optional[int]:
        return settings_store.get_premium_last_network_failure_ts()

    @staticmethod
    def save_last_network_failure_now() -> bool:
        return bool(settings_store.set_premium_last_network_failure_ts(int(time.time())))

    @staticmethod
    def clear_last_network_failure() -> bool:
        return bool(settings_store.set_premium_last_network_failure_ts(None))

    @staticmethod
    def get_pair_code() -> Optional[str]:
        return settings_store.get_premium_pair_code()

    @staticmethod
    def get_pair_expires_at() -> Optional[int]:
        return settings_store.get_premium_pair_expires_at()

    @staticmethod
    def set_pair_code(*, code: str, expires_at: int) -> bool:
        code = (code or "").strip().upper()
        try:
            expires_at_i = int(expires_at)
        except Exception:
            return False
        if not code or expires_at_i <= 0:
            return False
        return bool(settings_store.set_premium_pair_code(code=code, expires_at=expires_at_i))

    @staticmethod
    def clear_pair_code() -> bool:
        return bool(settings_store.set_premium_pair_code(code=None, expires_at=None))

    @staticmethod
    def get_premium_cache() -> Optional[Dict[str, Any]]:
        cache = settings_store.get_premium_cache()
        return cache if isinstance(cache, dict) else None

    @staticmethod
    def set_premium_cache(cache: Dict[str, Any]) -> bool:
        if not isinstance(cache, dict):
            return False
        return bool(settings_store.set_premium_cache(cache))

    @staticmethod
    def clear_premium_cache() -> bool:
        return bool(settings_store.set_premium_cache(None))

    @staticmethod
    def store_after_pairing(
        *,
        device_id: str,
        device_token: str,
        signed_payload: Dict[str, Any],
        kid: Optional[str],
        sig: Optional[str],
    ) -> bool:
        device_id = (device_id or "").strip()
        device_token = (device_token or "").strip()
        if not device_id or not device_token or not isinstance(signed_payload, dict):
            return False

        settings_store.set_premium_settings(
            {
                "device_id": device_id,
                "device_token": device_token,
                "last_check": datetime.now().isoformat(),
                "pair_code": None,
                "pair_expires_at": None,
                "premium_cache": PremiumStorage._cache_payload(
                    signed_payload=signed_payload,
                    kid=kid,
                    sig=sig,
                ),
            }
        )
        return True

    @staticmethod
    def store_status_active(*, signed_payload: Dict[str, Any], kid: Optional[str], sig: Optional[str]) -> bool:
        if not isinstance(signed_payload, dict):
            return False

        settings_store.set_premium_settings(
            {
                "last_check": datetime.now().isoformat(),
                "premium_cache": PremiumStorage._cache_payload(
                    signed_payload=signed_payload,
                    kid=kid,
                    sig=sig,
                ),
            }
        )
        return True

    @staticmethod
    def apply_status_inactive(*, message: str) -> bool:
        _ = message
        settings_store.set_premium_settings(
            {
                "last_check": datetime.now().isoformat(),
                "premium_cache": None,
            }
        )
        return True
