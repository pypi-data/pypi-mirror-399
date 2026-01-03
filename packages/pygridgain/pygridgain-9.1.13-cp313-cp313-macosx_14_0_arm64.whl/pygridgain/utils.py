# Copyright (C) GridGain Systems. All Rights Reserved.
# _________        _____ __________________        _____
# __  ____/___________(_)______  /__  ____/______ ____(_)_______
# _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
# / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
# \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
import builtins
import warnings
from functools import wraps
from ssl import SSLContext
from typing import Any, AsyncIterator, Mapping, Optional

from pygridgain.basic_authenticator import BasicAuthenticator
from pygridgain.error_code import ErrorCode
from pygridgain.ignite_error import IgniteError
from pygridgain.ssl_config import SSLConfig

# Implementation for Python 3.9
if not hasattr(builtins, "anext"):
    _sentinel = object()

    async def anext(iterator: AsyncIterator[Any], default: Any = _sentinel) -> Any:
        try:
            return await iterator.__anext__()
        except StopAsyncIteration:
            if default is not _sentinel:
                return default
            raise

else:
    anext = anext


def is_iterable(value: Any) -> bool:
    """Check if the value is iterable."""
    try:
        iter(value)
        return True
    except TypeError:
        return False


def deprecated(version, reason):
    def decorator_deprecated(fn):
        @wraps(fn)
        def wrapper_deprecated(*args, **kwds):
            warnings.warn(f"Deprecated since {version}. The reason: {reason}", category=DeprecationWarning)
            return fn(*args, **kwds)

        return wrapper_deprecated

    return decorator_deprecated


def ssl_wrap_socket(ssl_config: SSLConfig, socket):
    """Wrap socket in SSL wrapper."""
    context = create_ssl_context(ssl_config)

    return context.wrap_socket(sock=socket)


def create_ssl_context(ssl_config: SSLConfig) -> Optional[SSLContext]:
    """Create SSL context from SSL config."""
    if ssl_config is None:
        return None

    check_ssl_config(ssl_config)
    context = SSLContext(ssl_config.protocol_version)
    context.verify_mode = ssl_config.cert_reqs

    if ssl_config.ca_file:
        context.load_verify_locations(ssl_config.ca_file)
    if ssl_config.cert_file:
        context.load_cert_chain(ssl_config.cert_file, ssl_config.key_file, ssl_config.key_file_password)
    if ssl_config.ciphers:
        context.set_ciphers(ssl_config.ciphers)

    return context


def check_ssl_config(ssl_config: SSLConfig):
    """Validate SSL config."""
    if ssl_config is None:
        return

    if ssl_config.key_file and not ssl_config.cert_file:
        raise ValueError("cert_file must be specified")


def extra_from_connection_config(authenticator: Optional[BasicAuthenticator]) -> Mapping[str, str]:
    if authenticator is None:
        return {}

    if isinstance(authenticator, BasicAuthenticator):
        return {
            "authn-type": "basic",
            "authn-identity": authenticator.username,
            "authn-secret": authenticator.password,
        }

    raise IgniteError(ErrorCode.ILLEGAL_ARGUMENT, f"Authenticator is not supported: {authenticator}")
