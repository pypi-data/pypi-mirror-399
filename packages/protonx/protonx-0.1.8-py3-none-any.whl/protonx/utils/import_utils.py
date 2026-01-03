import importlib.util
import importlib.metadata
from packaging.version import Version
from packaging.specifiers import SpecifierSet

def is_torch_available():
    return importlib.util.find_spec("torch") is not None

def is_torchvision_available():
    return importlib.util.find_spec("torchvision") is not None

def require_version(requirement: str):
    """
    Example:
        require_version("torch>=2.0.0")
    """
    pkg, spec = requirement.split(">=")
    installed_version = importlib.metadata.version(pkg)

    if Version(installed_version) not in SpecifierSet(f">={spec}"):
        raise ImportError(
            f"{pkg} version {installed_version} does not satisfy >= {spec}. "
            f"Install with: pip install '{pkg}>={spec}'"
        )

