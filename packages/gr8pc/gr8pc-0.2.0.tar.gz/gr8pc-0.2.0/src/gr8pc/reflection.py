import logging
from typing import Type

from grpc import Server

from .service.base import BaseService

try:
    from grpc_reflection.v1alpha import reflection
except ImportError:
    raise ImportError(
        'grpcio-reflection is required for reflection support. '
        'Install with `reflection` extra: `pip install gr8pc[reflection]` or directly install '
        '`grpcio-reflection`.'
    )

logger = logging.getLogger(__name__)


def apply_reflection(server: Server, services: dict[str, Type[BaseService]]) -> None:
    service_names = []
    for service in services.values():
        if service.protos:
            service_names.extend(
                [svc.full_name for svc in service.protos.DESCRIPTOR.services_by_name.values()]
            )

    logger.info(f'Enabling reflection for services: {service_names}')

    service_names.append(reflection.SERVICE_NAME)
    reflection.enable_server_reflection(service_names, server)
