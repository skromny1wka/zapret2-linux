from __future__ import annotations

import asyncio
import unittest
from unittest.mock import patch


class TelegramProxySocks5Tests(unittest.TestCase):
    def test_proactor_connection_lost_reset_is_quiet_loop_failure(self) -> None:
        import telegram_proxy

        exc = ConnectionResetError("remote host closed connection")
        exc.winerror = 10054

        self.assertTrue(
            telegram_proxy._is_ignorable_asyncio_loop_exception(
                {
                    "message": "Exception in callback _ProactorBasePipeTransport._call_connection_lost()",
                    "exception": exc,
                    "handle": object(),
                }
            )
        )

    def test_handshake_timeout_is_quiet_protocol_failure(self) -> None:
        from telegram_proxy.proxy import socks5

        async def run_check() -> None:
            with (
                patch.object(socks5, "_do_handshake", side_effect=asyncio.TimeoutError),
                patch.object(socks5.log, "debug") as debug_log,
                patch.object(socks5.log, "exception") as exception_log,
            ):
                result = await socks5.handshake(object(), object())

            self.assertIsNone(result)
            debug_log.assert_called_once()
            exception_log.assert_not_called()

        asyncio.run(run_check())


if __name__ == "__main__":
    unittest.main()
