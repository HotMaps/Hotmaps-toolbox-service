from .exceptions import TimeOutException
from .restplus import handle_timeout_reached
import signal
from ..constants import DEFAULT_TIMEOUT


def timeout_signal_handler(signum, frame):
    """
    raise a timeout exception when the timeout value is reached
    :param signum:
    :param frame:
    :return:
    """
    raise TimeOutException('end of time')


def return_on_timeout_endpoint(timeout_value: int = DEFAULT_TIMEOUT):
    """
    A decorator to handle the return when a timeout occurs. It works only in API endpoints
    :param timeout_value:the timeout before leaving the function in seconds, default corresponding to the config file
    :return:
    """
    def decorate(f):
        def applicator(*args, **kwargs):
            try:
                signal.signal(signal.SIGALRM, timeout_signal_handler)
                signal.alarm(timeout_value)
                return f(*args, **kwargs)
            except TimeOutException:
                return handle_timeout_reached()

        return applicator

    return decorate