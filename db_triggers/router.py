import importlib
import inspect
import pkgutil

from alembic_utils.replaceable_entity import ReplaceableEntity


def discover_replaceable_entities():
    """Discover and return all ReplaceableEntity instances in the given package/module."""
    discovered_entities = []
    package_name = "db_triggers"
    try:
        module = importlib.import_module(package_name)
    except ImportError:
        return []

    # If it's a package, walk through submodules
    if hasattr(module, "__path__"):
        for _, mod_name, _ in pkgutil.walk_packages(
            module.__path__, package_name + "."
        ):
            mod = importlib.import_module(mod_name)
            for _, obj in inspect.getmembers(mod):
                if isinstance(obj, ReplaceableEntity):
                    discovered_entities.append(obj)
    else:
        # It's a module
        for _, obj in inspect.getmembers(module):
            if isinstance(obj, ReplaceableEntity):
                discovered_entities.append(obj)

    return discovered_entities
