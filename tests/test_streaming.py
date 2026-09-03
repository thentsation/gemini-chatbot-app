from utils.streaming import response_generator


def test_response_generator_yields_words_with_trailing_space() -> None:
    chunks = list(response_generator('olá tudo bem'))
    assert chunks == ['olá ', 'tudo ', 'bem ']


def test_response_generator_reassembles_to_original_words() -> None:
    text = 'um dois tres'
    assert ''.join(response_generator(text)).strip() == text


def test_response_generator_handles_empty_string() -> None:
    assert list(response_generator('')) == []
