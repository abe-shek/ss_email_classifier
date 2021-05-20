import os

from EmailClassifier import settings


def auto_str(cls):
    def __str__(self):
        return "%s(%s)" % (
            type(self).__name__,
            ", ".join("%s=%s" % item for item in vars(self).items()),
        )

    cls.__str__ = __str__
    return cls


class UploadFileType:
    FT_TEXT_EXT = '.txt'
    FT_ZIP_EXT = '.zip'


class Directory:
    DIR_MODEL_ROOT_PATH = os.path.join(settings.BASE_DIR, "model")
    DIR_Q_PATH = os.path.join(DIR_MODEL_ROOT_PATH, 'queue')
    DIR_SUCCESS_PATH = os.path.join(DIR_MODEL_ROOT_PATH, 'successful')
    DIR_ERROR_PATH = os.path.join(DIR_MODEL_ROOT_PATH, 'errors')


class UploadStatus:
    UP_STATUS_NOT_UPLOADED = 0
    UP_STATUS_PROCESSING = 1
    UP_STATUS_PROCESSED = 2
    UP_STATUS_ERROR = 3


@auto_str
class Error:
    def __init__(self, err_code, err_message):
        self.code = err_code
        self.message = err_message


class ErrorCodes:
    E_METHOD_CALL_FAILED = 0x1001
    E_WRONG_THREAD = 0x2001

