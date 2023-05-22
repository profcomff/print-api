from print_service.settings import get_settings


settings = get_settings()


class ObjectNotFound(Exception):
    pass


class TerminalTokenNotFound(ObjectNotFound):
    pass


class TerminalQRNotFound(ObjectNotFound):
    pass


class PINNotFound(ObjectNotFound):
    def __init__(self, pin: str):
        self.pin = pin


class UserNotFound(ObjectNotFound):
    pass


class FileNotFound(ObjectNotFound):
    def __init__(self, count: int):
        self.count = count


class TooManyPages(Exception):
    def __init__(self):
        super().__init__(f'Content too large, count of page: {settings.MAX_PAGE_COUNT} is allowed')


class TooLargeSize(Exception):
    def __init__(self):
        super().__init__(f'Content too large, {settings.MAX_SIZE} bytes allowed')


class InvalidPageRequest(Exception):
    def __init__(self):
        super().__init__(f'Invalid format')


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


class InvalidType(Exception):
    def __init__(self, content_type: str):
        super().__init__(
            f'Only {", ".join(settings.CONTENT_TYPES)} files allowed, but {content_type} was recieved'
        )


class AlreadyUploaded(Exception):
    def __init__(self):
        super().__init__(f'File has been already uploaded')


class IsCorrupted(Exception):
    def __init__(self):
        super().__init__(f'File is corrupted')


class IsNotUploaded(Exception):
    def __init__(self):
        super().__init__(f'File has not been uploaded yet')


class UnprocessableFileInstance(Exception):
    def __init__(self):
        super().__init__(f'Unprocessable file instance')
