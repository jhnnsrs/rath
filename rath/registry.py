import asyncio
from typing import Dict, Type
from herre import get_current_herre
from rath.rath import Rath


class NoRathRegistered(Exception):
    pass


class RathRegistry:
    def __init__(self) -> None:
        self.domainRathClassMap: Dict[str, Type[Rath]] = {}
        self.domainRathInstanceMap: Dict[str, Rath] = {}

    def register_rath(self, domain, wardClass: Type[Rath]):
        assert (
            domain not in self.domainRathClassMap
        ), "We cannot register another Ward for this domain"
        self.domainRathClassMap[domain] = wardClass

    def get_rath_class(self, domain) -> Rath:
        try:
            return self.domainRathClassMap[domain]
        except KeyError as e:
            raise NoRathRegistered(f"No Rath registered for domain {domain}") from e

    def get_rath_instance(self, domain) -> Rath:
        if domain in self.domainRathInstanceMap:
            return self.domainRathInstanceMap[domain]
        self.domainRathInstanceMap[domain] = self.domainRathClassMap[domain]()
        return self.domainRathInstanceMap[domain]

    # Handling Connection

    async def connect_all(self):
        unconnected_wards = [
            ward
            for key, ward in self.domainRathInstanceMap.items()
            if not ward.connected
        ]
        await asyncio.gather(*[ward._connect() for ward in unconnected_wards])

    async def unconnect_all(self):
        connected_wards = [
            ward for key, ward in self.domainRathInstanceMap.items() if ward.connected
        ]
        await asyncio.gather(*[ward._disconnect() for ward in connected_wards])


RATH_REGISTRY = None


def get_rath_registry():
    global RATH_REGISTRY
    if not RATH_REGISTRY:
        RATH_REGISTRY = RathRegistry()
    return RATH_REGISTRY
