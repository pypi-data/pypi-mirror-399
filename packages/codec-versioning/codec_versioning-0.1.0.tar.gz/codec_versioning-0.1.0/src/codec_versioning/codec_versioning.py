"""Machinery for managing multiple encoding versions.

Contains the Codec class for versioning alternative pairs of
encoding and decoding functions.

When encoding using a supplied codec, the codec version is encoded into the
encoded data.
When decoding, the correct codec is determined from the encoded data.
"""

from typing import TypeVar, Generic, Callable, Type
from types import ModuleType
from brenthy_tools_beta.utils import (
    from_b255_no_0s,
    to_b255_no_0s,
)

T = TypeVar("T")


class Codec(Generic[T]):
    """Represents a versioned pair of encoding and decoding functions."""

    version: int
    obj_type: Type[T]
    encoder: Callable[[T], bytes]
    decoder: Callable[[bytes], T]

    def __init__(
        self,
        version: int,
        obj_type: Type[T],
        encoder: Callable[[T], bytes],
        decoder: Callable[[bytes], T],
    ):
        self.version = version
        self.obj_type = obj_type
        self.encoder = encoder
        self.decoder = decoder


# load encoding modules into Codecs
def load_codec_module(mod: ModuleType):
    """Create a Codec object from the given module."""
    return Codec[mod.CODEC_OBJ_TYPE](
        version=mod.CODEC_VERSION,
        obj_type=mod.CODEC_OBJ_TYPE,
        encoder=mod.encode,
        decoder=mod.decode,
    )


def load_codec_modules(modules: list[ModuleType]) -> dict[int, Codec]:
    """Create a dictionary of Codecs from the given modules."""
    codecs: dict[int, Codec] = {}
    for mod in modules:
        codec = load_codec_module(mod)
        if codec.version in codecs:
            raise Exception(f"Duplicate codec version: {codec.version}")
        codecs.update({codec.version: codec})
    return codecs


class DecodeError(Exception):
    """When decoding fails."""

    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return f"Endra Message Encoding DecodeError: {self.message}"


def add_format_version(data: bytes, format_version: int) -> bytes:
    """Add the encoding version to encoded data."""
    return bytes(to_b255_no_0s(format_version) + bytearray([0]) + data)


def extract_format_version(data: bytes) -> tuple[int, bytes]:
    """Extract the encoding version from versioned encoded data."""
    _data = bytearray(data)
    try:
        i = _data.index(0)
    except IndexError:
        raise DecodeError("Failed to decode encoding version.")

    format_version = from_b255_no_0s(_data[:i])
    _data = _data[i + 1 :]
    return format_version, _data


def encode_versioned(obj, codec: Codec) -> bytes:
    """Encode the provided object, along with the used Codec version."""
    data = codec.encoder(obj)
    if not isinstance(obj, codec.obj_type):
        raise TypeError(
            f"The type of the object to encode (`{type(obj)}` "
            f"does not match the type of the codec (`{codec.obj_type}`))"
        )
    return add_format_version(data, codec.version)


def decode_versioned(data: bytes, codecs: dict[int, Codec]):
    """Decode data, automatically determining the correct codec to use."""
    if not (isinstance(data, bytes) or isinstance(data, bytearray)):
        raise TypeError(f"Data must be of type bytes, not{type(data)}")
    version, data = extract_format_version(data)
    try:
        codec = codecs[version]
    except IndexError:
        raise DecodeError(f"Unknown encoding version for Message: {version}")
    result = codec.decoder(data)
    if not isinstance(result, codec.obj_type):
        raise DecodeError(
            f"Decoder returned an unexpected type: `{result}`. "
            f"Expected `{codec.obj_type}`"
        )
    return result
