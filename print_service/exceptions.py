from print_service.settings import get_settings


settings = get_settings()


class TooManyPages(Exception):
    def __init__(self):
        super().__init__(f'Content too large, count of page: {settings.MAX_PAGE_COUNT} is allowed')


class TooLargeSize(Exception):
    def __init__(self):
        super().__init__(f'Content too large, {settings.MAX_SIZE} bytes allowed')


class InvalidPageRequest(Exception):
    def __init__(self):
        super().__init__(f'Invalid format')


class TerminalNotFound(Exception):
    def __init__(self, type: str):
        super().__init__(f'Terminal is not found by {type}')


class UserNotFound(Exception):
    def __init__(self):
        super().__init__(f'User is not found')


class UnionStudentDuplicate(Exception):
    def __init__(self):
        super().__init__('Duplicates by union_numbers or student_numbers')


class NotInUnion(Exception):
    def __init__(self):
        super().__init__(f'User is not found in trade union list')


class PINGenerateError(Exception):
    def __init__(self):
        super().__init__(f'Can not generate PIN. Too many users?')


class FileIsNotReceived(Exception):
    def __init__(self):
        super().__init__(f'No file was recieved')


class PINNotFound(Exception):
    def __init__(self, pin: str):
        super().__init__(f'Pin {pin} is not found')


class InvalidType(Exception):
    def __init__(self, content_type: str):
        super().__init__(
            f'Only {", ".join(settings.CONTENT_TYPES)} files allowed, but {content_type} was recieved'
        )


class AlreadyUpload(Exception):
    def __init__(self):
        super().__init__(f'File has been already uploaded')


class IsCorrupt(Exception):
    def __init__(self):
        super().__init__(f'File is corrupted')
