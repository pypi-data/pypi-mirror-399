import inspect
from collections import defaultdict
from collections.abc import AsyncGenerator, Awaitable, Generator, Iterator
from types import FunctionType, ModuleType
from typing import Any, TypeVar

import structlog

from asgikit.sync import run_sync

from zayt.util.maybe_async import call_maybe_async
from zayt.util.package_scan import scan_packages
from zayt.di.decorator import ATTRIBUTE_DI_SERVICE
from zayt.di.decorator import service as service_decorator
from zayt.di.error import (
    DependencyLoopError,
    IncompatibleDependencyScopeError,
    ScopedServiceWithoutContextError,
    ServiceNotFoundError,
    ServiceWithoutDecoratorError,
)
from zayt.di.interceptor import Interceptor
from zayt.di.service.model import InjectableType, ServiceDependency, ServiceSpec
from zayt.di.service.parse import parse_service_spec
from zayt.di.service.registry import ServiceRegistry

logger = structlog.get_logger(__name__)

T = TypeVar("T")


def _is_service(arg) -> bool:
    return (inspect.isfunction(arg) or inspect.isclass(arg)) and hasattr(
        arg, ATTRIBUTE_DI_SERVICE
    )


class Container:
    def __init__(self):
        self.registry = ServiceRegistry()
        self.cache: dict[int | None, dict[tuple[type, str | None], Any]] = defaultdict(
            dict
        )
        self.finalizers: dict[int | None, list[Awaitable]] = defaultdict(list)
        self.interceptors: list[type[Interceptor]] = []

    def scan(self, *args: str | ModuleType):
        for item in scan_packages(*args, predicate=_is_service):
            self.register(item)

    def register(self, injectable: InjectableType):
        service_info = getattr(injectable, ATTRIBUTE_DI_SERVICE, None)

        if not service_info:
            raise ServiceWithoutDecoratorError(injectable)

        spec = parse_service_spec(injectable, *service_info)
        service_iface = spec.service
        service_impl = spec.impl
        name = spec.name

        self.registry[service_iface, name] = spec

        if name and service_impl:
            logger.debug(
                "service registered with implementation and name",
                service=f"{injectable.__module__}.{injectable.__qualname__}",
                implentation=f"{service_impl.__module__}.{service_impl.__qualname__}",
                name=name,
            )
        elif name:
            logger.debug(
                "service registered with name",
                service=f"{injectable.__module__}.{injectable.__qualname__}",
                name=name,
            )
        elif service_impl:
            logger.debug(
                "service registered with implementation",
                service=f"{injectable.__module__}.{injectable.__qualname__}",
                implentation=f"{service_impl.__module__}.{service_impl.__qualname__}",
            )
        else:
            logger.debug(
                "service registered",
                service=f"{injectable.__module__}.{injectable.__qualname__}",
            )

    def define(
        self,
        service_type: type,
        instance: Any,
        *,
        name: str = None,
        context: Any = None,
    ):
        cache_key = id(context) if context else None
        self.cache[cache_key][service_type, name] = instance

        if name:
            logger.debug(
                "service defined",
                service=f"{service_type.__module__}.{service_type.__qualname__}",
                name=name,
            )
        else:
            logger.debug(
                "service defined",
                service=f"{service_type.__module__}.{service_type.__qualname__}",
            )

    def interceptor(self, interceptor: type[Interceptor]):
        self.register(
            service_decorator(
                interceptor,
                provides=Interceptor,
                name=f"{interceptor.__module__}.{interceptor.__qualname__}",
            )
        )
        self.interceptors.append(interceptor)

        logger.debug(
            "interceptor registered",
            interceptor=f"{interceptor.__module__}.{interceptor.__qualname__}",
        )

    def has(self, service_type: type, name: str = None) -> bool:
        definition = self.registry.get(service_type, name=name)
        return definition is not None

    def iter_service(
        self, service_type: type
    ) -> Iterator[tuple[type | FunctionType, str | None]]:
        record = self.registry.services.get(service_type)
        if not record:
            raise ServiceNotFoundError(service_type)

        for name, definition in record.providers.items():
            yield definition.impl, name

    def iter_all_services(
        self,
    ) -> Iterator[tuple[type, type | FunctionType | None, str | None]]:
        for _interface, record in self.registry.services.items():
            for name, definition in record.providers.items():
                yield definition.service, definition.impl, name

    async def get(
        self,
        service_type: type[T],
        *,
        name: str = None,
        optional=False,
        context: Any = None,
    ) -> T:
        dependency = ServiceDependency(service_type, name=name, optional=optional)
        return await self._get(dependency, context=context)

    async def finalize(self, context: Any = None):
        if context is not None:
            context_id = id(context)
            for finalizer in reversed(self.finalizers[context_id]):
                await finalizer

            del self.finalizers[context_id]
            return

        for context_id in self.finalizers:
            for finalizer in reversed(self.finalizers[context_id]):
                await finalizer

    def _get_from_cache(
        self,
        service_type: type[T],
        name: str | None,
        context: Any = None,
    ) -> T | None:
        if context is not None:
            context_id = id(context)
            if instance := self.cache[context_id].get((service_type, name)):
                return instance

        return self.cache[None].get((service_type, name))

    async def _get(
        self,
        dependency: ServiceDependency,
        context: Any = None,
        stack: list[tuple[type, str | None]] = None,
    ) -> Any | None:
        service_type, service_name, optional = (
            dependency.service,
            dependency.name,
            dependency.optional,
        )

        # check if service exists in cache
        if instance := self._get_from_cache(service_type, service_name, context):
            return instance

        try:
            service_spec = self.registry.get(service_type, service_name)
            if not service_spec:
                raise ServiceNotFoundError(service_type, service_name)
        except ServiceNotFoundError:
            if optional:
                return None
            raise

        stack = stack or []

        if stack:
            parent_service, parent_name = stack[-1]
            parent_spec = self.registry.get(parent_service, parent_name)
            if service_spec.scoped and not parent_spec.scoped:
                raise IncompatibleDependencyScopeError(
                    parent_service, service_type, parent_name
                )

        if (service_type, service_name) in stack:
            raise DependencyLoopError(stack, (service_type, service_name))

        stack.append((service_type, service_name))
        instance = await self._create_service(service_spec, context, stack)
        stack.pop()

        return instance

    async def _get_dependent_services(
        self,
        service_spec: ServiceSpec,
        context: Any | None,
        stack: list,
    ) -> dict[str, Any]:
        return {
            name: await self._get(dep, context, stack)
            for name, dep in service_spec.dependencies
        }

    async def _create_service(
        self,
        service_spec: ServiceSpec,
        context: Any | None,
        stack: list[tuple[type[T], str]],
    ) -> T:
        name = service_spec.name

        if not service_spec.scoped:
            context = None
        elif context is None:
            raise ScopedServiceWithoutContextError(service_spec.service)

        context_id = id(context) if context else None

        if factory := service_spec.factory:
            dependencies = await self._get_dependent_services(
                service_spec, context, stack
            )

            instance = await call_maybe_async(factory, **dependencies)
            if inspect.isgenerator(instance):
                generator = instance
                instance = await run_sync(next, generator)
                self._setup_generator_finalizer(generator, context)
            elif inspect.isasyncgen(instance):
                generator = instance
                instance = await anext(generator)
                self._setup_asyncgen_finalizer(generator, context)

            self.cache[context_id][service_spec.service, name] = instance
        else:
            instance = service_spec.impl()
            self.cache[context_id][service_spec.service, name] = instance

            dependencies = await self._get_dependent_services(
                service_spec, context, stack
            )

            for name, dep_service in dependencies.items():
                setattr(instance, name, dep_service)

            if initializer := service_spec.initializer:
                await call_maybe_async(initializer, instance)

            self._setup_finalizer(service_spec, instance, context_id)

        if service_spec.service is not Interceptor:
            await self._run_interceptors(instance, service_spec.service)

        return instance

    def _setup_finalizer(
        self, service_spec: ServiceSpec, instance: Any, context_id: int | None
    ):
        if finalizer := service_spec.finalizer:
            self.finalizers[context_id].append(call_maybe_async(finalizer, instance))

    def _setup_generator_finalizer(self, gen: Generator, context: Any | None):
        context_id = id(context) if context else None
        self.finalizers[context_id].append(run_sync(next, gen, None))

    def _setup_asyncgen_finalizer(self, gen: AsyncGenerator, context: Any | None):
        context_id = id(context) if context else None
        self.finalizers[context_id].append(anext(gen, None))

    async def _run_interceptors(self, instance: Any, service_type: type):
        for cls in self.interceptors:
            interceptor = await self.get(
                Interceptor, name=f"{cls.__module__}.{cls.__qualname__}"
            )
            await call_maybe_async(interceptor.intercept, instance, service_type)
