from print_service.settings import get_settings
import pytest
import starlette


class TestFile:
    url = '/file'
    settings = get_settings()
