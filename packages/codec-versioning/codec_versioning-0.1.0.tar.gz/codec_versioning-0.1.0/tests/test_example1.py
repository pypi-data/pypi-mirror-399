"""Run the example at ./examples/example1.py"""

import _auto_run_with_pytest  # noqa
from example1.example_encoding import encode, decode, CODECS
from example1.example_model import ExampleModel
from codec_versioning import encode_versioned


def test_default_encoding():
    model = ExampleModel(1, 2)

    assert decode(encode(model)) == model


def test_all_codecs():
    model = ExampleModel(1, 2)
    for version, codec in CODECS.items():
        assert decode(encode_versioned(model, codec)) == model
