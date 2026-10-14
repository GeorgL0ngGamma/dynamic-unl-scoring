"""Crawl client for validator IP resolution.

Probes each topology node's /crawl endpoint on port 2559 to extract
pubkey_validator, mapping validator master keys to their IP addresses.
"""

import logging
from typing import Optional

import httpx

from scoring_service.config import settings
from scoring_service.constants import PEER_PROTOCOL_PORT

logger = logging.getLogger(__name__)


def _malformed(url: str, field: str, value: object, expected: str) -> None:
    """Log a malformed /crawl response and return None (no pubkey)."""
    kind = "an empty string" if value == "" else type(value).__name__
    logger.warning(
        "Ignoring malformed /crawl response from %s — %s is %s, expected %s",
        url,
        field,
        kind,
        expected,
    )
    return None


class CrawlClient:
    """Resolves validator IPs by probing topology nodes' /crawl endpoints."""

    def __init__(self):
        self._client = httpx.Client(
            timeout=settings.http_request_timeout,
            verify=False,
        )

    def close(self):
        self._client.close()

    def _probe_node(self, ip: str, port: int) -> Optional[str]:
        """Probe a single node's /crawl endpoint. Returns pubkey_validator or None.

        The body comes from an arbitrary peer, so a non-object body, a
        non-object "server" section, or a pubkey_validator that is present
        but not a non-empty string is logged and treated as no pubkey
        instead of raising and aborting the rest of the crawl.
        """
        url = f"https://{ip}:{port}/crawl"
        try:
            response = self._client.get(url)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                return _malformed(url, "body", data, "an object")
            server = data.get("server", {})
            if not isinstance(server, dict):
                return _malformed(url, "server", server, "an object")
            if "pubkey_validator" not in server:
                return None
            pubkey = server["pubkey_validator"]
            if not isinstance(pubkey, str) or not pubkey:
                return _malformed(
                    url, "server.pubkey_validator", pubkey, "a non-empty string"
                )
            return pubkey
        except (httpx.HTTPError, httpx.TimeoutException, ValueError) as exc:
            logger.warning("Failed to probe %s — %s", url, exc)
            return None

    def resolve_validators(
        self, topology_nodes: list[dict], master_keys: set[str]
    ) -> tuple[dict[str, str], list[dict]]:
        """Probe each topology node's /crawl endpoint.

        Returns (resolved map {master_key: ip}, raw probe results list).
        Nodes that are unreachable, lack pubkey_validator, or aren't
        validators are skipped from the resolved map but still recorded
        in the raw probe results.
        """
        resolved: dict[str, str] = {}
        raw_probes: list[dict] = []
        probed = 0

        for node in topology_nodes:
            ip = node.get("ip")
            if not ip:
                continue

            port = node.get("port") or PEER_PROTOCOL_PORT
            probed += 1
            pubkey = self._probe_node(ip, port)

            raw_probes.append({
                "ip": ip,
                "port": port,
                "pubkey_validator": pubkey,
            })

            if pubkey and pubkey in master_keys:
                resolved[pubkey] = ip
                logger.info("Resolved validator %s → %s", pubkey[:12] + "...", ip)

        logger.info(
            "Resolved %d/%d validator IPs from %d topology nodes probed",
            len(resolved),
            len(master_keys),
            probed,
        )
        return resolved, raw_probes
