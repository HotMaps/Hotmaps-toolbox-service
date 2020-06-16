from .exceptions import TimeOutException
from .restplus import handle_timeout_reached
import signal


def handler(signum, frame):
    """
    raise a timeout exception when the timeout value is reached
    :param signum:
    :param frame:
    :return:
    """
    raise TimeOutException("end of time")


def return_on_timeout(timeout_value):
    """
    A decorator to handle the return when a timeout occurs
    :param timeout_value:the timeout before leaving the function in seconds
    :return:
    """
    def decorate(f):
        def applicator(*args, **kwargs):
            try:
                signal.signal(signal.SIGALRM, handler)
                signal.alarm(timeout_value)
                f(*args, **kwargs)
            except TimeOutException:
                return handle_timeout_reached()

        return applicator

    return decorate