from typing import Type

from print_service.settings import get_settings


settings = get_settings()


class PrintAPIError(Exception):
    eng: str
    ru: str

    def __init__(self, eng: str, ru: str) -> None:
        self.eng = eng
        self.ru = ru
        super().__init__(eng)


class ObjectNotFound(PrintAPIError):
    def __init__(self, obj: type, obj_id_or_name: int | str):
        super().__init__(
            f"Object {obj.__name__} {obj_id_or_name=} not found",
            f"Объект {obj.__name__} с идентификатором {obj_id_or_name} не найден",
        )


class AlreadyExists(PrintAPIError):
    def __init__(self, obj: type, obj_id_or_name: int | str):
        super().__init__(
            f"Object {obj.__name__}, {obj_id_or_name=} already exists",
            f"Объект {obj.__name__} с идентификатором {obj_id_or_name=} уже существует",
        )


class TerminalTokenNotFound(ObjectNotFound):
    def __init__(self, token_id: int | str):
        super().__init__(type(self), token_id)


class TerminalQRNotFound(ObjectNotFound):
    def __init__(self, qr_id: int | str):
        super().__init__(type(self), qr_id)


class PINNotFound(ObjectNotFound):
    def __init__(self, pin: str):
        self.pin = pin
        super().__init__(type(self), pin)


class UserNotFound(ObjectNotFound):
    def __init__(self, user_id: int | str):
        super().__init__(type(self), user_id)


class FileNotFound(ObjectNotFound):
    def __init__(self, file_id: int | str):
        super().__init__(type(self), file_id)


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
