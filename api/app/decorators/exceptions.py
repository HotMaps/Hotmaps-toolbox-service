class IntersectionException(Exception):
    '''
    Exception raised when the points are crossing themself
    '''
    pass


class HugeRequestException(Exception):
    '''
    Exception raised when the request is too big
    '''
    pass


class NotEnoughPointsException(Exception):
    '''
    Exception raised when the number of points is inferior or egal to 2
    '''
    pass


class ParameterException(Exception):
    '''
    Exception raised when the parameters entered are false
    '''
    pass


class TimeoutException(Exception):
    '''
    Exception raised when the request took too many time
    '''
    pass

class RequestException(Exception):
    '''
    Exception raised by default when a request fail
    '''
    pass

class ValidationError(ValueError):
    pass





