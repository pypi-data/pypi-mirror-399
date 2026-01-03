import importlib
from typing import Optional
from django.urls import path, include


def add_path(
    path_dir: str,
    application: str,
    namespace: Optional[str] = None,
):
    """
    Registra dinámicamente las URLs de una aplicación Django.

    Permite incluir rutas desde apps sin importarlas directamente
    en el urls.py principal o en urls internos de otras apps.

    Args:
        path_dir (str):
            Prefijo de URL. Ej: "api/users/"
        application (str):
            Nombre del módulo de la app. Ej: "users"
        namespace (str, opcional):
            Namespace para include(). Si no se proporciona,
            se usa el nombre de la aplicación.

    Raises:
        ModuleNotFoundError:
            - Si la app no existe
            - Si la app existe pero no tiene urls.py
    """

    namespace = namespace or application

    try:
        urls_module = importlib.import_module(f"{application}.urls")
    except ModuleNotFoundError as e:
        missing = str(e)

        if f"{application}.urls" in missing:
            raise ModuleNotFoundError(
                f"La aplicación '{application}' existe, pero no define un archivo "
                f"'urls.py'.\n"
                f"Solución: crea '{application}/urls.py' o elimina el add_path()."
            ) from e

        raise ModuleNotFoundError(
            f"No se pudo importar la aplicación '{application}'.\n"
            f"Verifica que esté incluida en INSTALLED_APPS "
            f"y que el nombre del módulo sea correcto."
        ) from e

    return path(
        path_dir,
        include((urls_module, application), namespace=namespace)
    )
