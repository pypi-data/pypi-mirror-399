from PyInstaller.utils.hooks import get_hook_config, collect_data_files
import os

# SOURCEdefender PyInstaller Hook
# Declares all dependencies used by SOURCEdefender's compiled .so files
# that PyInstaller cannot automatically detect

datas = []

hiddenimports = [
    # Core dependencies from requirements.txt
    "msgpack",
    "msgpack.exceptions",
    "feedparser",
    "cryptography",
    "cryptography.hazmat",
    "cryptography.hazmat.primitives",
    "cryptography.hazmat.primitives.ciphers",
    "cryptography.hazmat.primitives.ciphers.algorithms",
    "cryptography.hazmat.primitives.ciphers.modes",
    "cryptography.hazmat.primitives.ciphers.aead",
    "cryptography.hazmat.primitives.kdf",
    "cryptography.hazmat.primitives.kdf.pbkdf2",
    "cryptography.hazmat.primitives.kdf.hkdf",
    "cryptography.hazmat.primitives.hashes",
    "cryptography.hazmat.primitives.hmac",
    "cryptography.hazmat.backends",
    "cryptography.hazmat.backends.openssl",
    "boltons",
    "boltons.timeutils",
    "environs",
    "psutil",
    "ntplib",
    "requests",
    "requests.adapters",
    "requests.packages.urllib3.util.retry",
    "packaging",
    "packaging.version",
    "setuptools",
    "setuptools.command.easy_install",
    "wheel",
    "docopt",
    # SOURCEdefender internal modules
    "sourcedefender.engine",
    # Standard library modules used by SOURCEdefender
    "os",
    "sys",
    "datetime",
    "threading",
    "subprocess",
    "re",
    "gc",
    "marshal",
    "zlib",
    "hashlib",
    "inspect",
    "types",
    "importlib",
    "importlib.abc",
    "importlib.util",
    "ast",
    "textwrap",
    "logging",
    "pathlib",
    "tempfile",
    "glob",
    "shutil",
    "socket",
    # Crypto and encoding
    "base64",
    "uuid",
    # Network utilities
    "urllib3",
    "urllib3.exceptions",
    "urllib.request",
    "urllib.parse",
    "certifi",
    # Environment and configuration
    "dotenv",
    "marshmallow",
    # Additional security-critical modules
    "platform",
    "time",
    "traceback",
    "warnings",
    "weakref",
    "copy",
    "collections",
    "itertools",
    "functools",
    # Anti-debugging protection modules
    "ctypes",
    "struct",
    "signal",
    "atexit",
    # Windows-specific modules
    "winreg",
    "_winreg",
    # PyInstaller integration
    "PyInstaller",
    "PyInstaller.__main__",
]

# Binary dependencies (if any)
binaries = []

# Runtime hooks for critical modules
runtime_hooks = []
