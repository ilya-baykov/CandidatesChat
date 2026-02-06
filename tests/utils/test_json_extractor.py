from core.utilities.json_extractor import JsonExtractor


def test_extract_json_from_text():
    """
    JSON корректно извлекается из произвольного текста.
    """

    text = "Ответ от AI: {\"key\": 123, \"value\": \"test\"} конец"
    result = JsonExtractor.extract_json(text)

    assert result == {"key": 123, "value": "test"}


def test_extract_json_returns_none_if_no_json_found():
    """
    Если JSON в тексте отсутствует — возвращается None.
    """

    text = "Просто текст без JSON"
    result = JsonExtractor.extract_json(text)

    assert result is None


def test_extract_json_returns_none_if_json_invalid():
    """
    Некорректный JSON обрабатывается безопасно.
    """

    text = "Текст {bad json"
    result = JsonExtractor.extract_json(text)

    assert result is None


def test_extract_json_returns_none_if_text_empty():
    """
    Пустой текст — None.
    """

    result = JsonExtractor.extract_json("")
    assert result is None
