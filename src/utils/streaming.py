"""Turns a full response string into a word-by-word generator for st.write_stream."""

import time
from collections.abc import Iterator


def response_generator(response: str) -> Iterator[str]:
    for word in response.split():
        yield word + ' '
        time.sleep(0.05)
