import functools
import inspect
from typing import Any, Callable, Generator, Iterator, Type, TypeVar, Coroutine

from src.application.executor.commands import BaseCommand
from src.application.executor.state import ExecutorState

TDependency = TypeVar("TDependency")

DependencyType = (
        TDependency
        | Callable[[Any], TDependency]
        | Generator[TDependency, None, None]
        | Iterator[TDependency]
)


class Executor:
    def __init__(self, state: ExecutorState):
        self.dependencies: dict[Type, Any] = {}
        self.handlers: dict[Type[BaseCommand], Callable[[BaseCommand], Any]] = {}
        self.state = state
        self.register_dependency(ExecutorState, self.state)

    def register_dependency(
            self, interface: Type, dependency: Any, cache: bool = False
    ) -> None:
        if isinstance(dependency, interface):
            self.dependencies[interface] = lambda: dependency
            return

        if inspect.isgenerator(dependency) or inspect.isgeneratorfunction(dependency):
            deps_signature = dict(inspect.signature(dependency).parameters)

            def wrapper():
                deps = {}
                for key, dep in deps_signature.items():
                    deps[key] = self.dependencies[dependency.annotation]
                print(deps)
                return dependency(**deps)

            if cache:
                def cached_generator(d: Generator):
                    _result = [None]

                    def wrapped() -> TDependency:
                        if len(_result) != 0:
                            return _result[0]
                        try:
                            _result[0] = next(d)
                            return _result[0]
                        except StopIteration:
                            return _result[0]

                    return wrapped

                self.dependencies[interface] = cached_generator(wrapper())
            else:
                self.dependencies[interface] = wrapper

            return

        if isinstance(dependency, Callable):
            if cache:
                self.dependencies[interface] = functools.cache(dependency)
            else:
                self.dependencies[interface] = dependency
            return

    def register_handler(self, command_type: Type[BaseCommand], handler: Callable) -> \
            Callable[[BaseCommand], Coroutine]:
        dependencies = inspect.signature(handler)
        accept_command = False
        accepted_dependencies = {}
        for name, dependency in dependencies.parameters.items():
            if issubclass(dependency.annotation, BaseCommand):
                accept_command = True
                continue
            if dependency.annotation not in self.dependencies:
                raise ValueError(f"{dependency.annotation} is not registered")

            accepted_dependencies[name] = self.dependencies[dependency.annotation]

        if not accept_command:
            raise SyntaxError("handler should accept an instance of BaseCommand")

        async def wrapped(command: command_type) -> None:
            if inspect.iscoroutinefunction(handler):
                return await handler(command, **{
                key: dep() for key, dep in accepted_dependencies.items()
            })
            return handler(command, **{
                key: dep() for key, dep in accepted_dependencies.items()
            })

        self.handlers[command_type] = wrapped
        return wrapped

    async def execute_command(self, command: BaseCommand) -> None:
        await self.handlers[type(command)](command)
