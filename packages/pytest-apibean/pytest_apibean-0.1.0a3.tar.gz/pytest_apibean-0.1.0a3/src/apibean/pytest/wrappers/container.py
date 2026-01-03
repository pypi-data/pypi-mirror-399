from dependency_injector import containers, providers

class ServiceWrappingMeta(containers.DeclarativeContainer.__class__):
    """
    Metaclass for dynamically wrapping service providers in a derived container.

    ``ServiceWrappingMeta`` is a specialized metaclass built on top of
    ``dependency_injector.containers.DeclarativeContainer`` that enables
    automatic wrapping of service providers inherited from a parent container.

    Its primary purpose is to adapt existing application containers for
    testing scenarios without modifying the original container definitions.

    When applied, this metaclass inspects the parent container and replaces
    selected providers (by naming convention) with wrapped providers that
    inject additional runtime context, such as an API invoker or test-specific
    dependencies.

    Key behaviors:

    - Identifies the nearest parent class that is a ``DeclarativeContainer``
    - Selects providers whose attribute names match a configurable suffix
      (default: ``"_service"``)
    - Wraps each matched provider using ``providers.Callable`` and a
      user-supplied injection function
    - Preserves the original provider interface while extending its behavior

    The wrapping process is entirely declarative and occurs at container
    class creation time, requiring no changes to the application container
    itself.

    Typical use cases include:

    - Injecting test-only collaborators into service instances
    - Attaching API clients or request invokers to domain services
    - Adapting production containers for integration or end-to-end tests
    - Providing controlled hooks for testing cross-cutting concerns

    Configuration parameters (passed as metaclass keyword arguments):

    - ``injected_func_name``:
        Name of the function used to inject additional context into each
        service instance. The function must accept the original service
        instance and the injected object, and return the modified service.

    - ``target_name_suffix``:
        Suffix used to select which providers from the parent container
        should be wrapped. Defaults to ``"_service"``.

    ``ServiceWrappingMeta`` is intentionally generic and framework-agnostic
    beyond ``dependency-injector``, making it suitable for reuse across
    different Apibean testing, mocking, and demo environments.
    """

    def __new__(cls, name, bases, namespace, **kwargs):
        injected_func_name = kwargs.pop("injected_func_name", None)
        target_name_suffix = kwargs.pop("target_name_suffix", "_service")

        _cls = super().__new__(cls, name, bases, namespace) # pylint: disable=E1121

        # Find the parent Container class
        parent_container = None
        for base in bases:
            if issubclass(base.__class__, containers.DeclarativeContainer.__class__):
                parent_container = base
                break

        if not parent_container:
            return _cls

        if injected_func_name:
            # Retrieve the user-defined inject function from the namespace
            # or inherited from the class
            inject_func = namespace.get(injected_func_name) or getattr(_cls, injected_func_name)

            # Automatically wrap all providers from the parent Container
            # whose names end with the given suffix (e.g. "_service")
            for attr_name, provider in parent_container.providers.items():
                if attr_name.endswith(target_name_suffix):
                    wrapped = providers.Callable(inject_func, provider, _cls.api_invoker)
                    setattr(_cls, attr_name, wrapped)

        return _cls
