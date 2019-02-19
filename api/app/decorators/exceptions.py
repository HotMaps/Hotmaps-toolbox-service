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


class ActivationException(Exception):
    '''
    Exception raised when an error occured during the user activation
    '''
    pass


class UserExistingException(Exception):
    '''
    Exception raised when someone try to register the same e-mail twice
    '''
    pass


class WrongCredentialException(Exception):
    '''
    Exception raised when the credentials are not correct
    '''
    pass


class UserUnidentifiedException(Exception):
    '''
    Exception raised when the user is not connected and has to be
    '''
    pass


class UserDoesntOwnUploadsException(Exception):
    '''
    Exception raised when the user try to interact with an uploads that does not belongs to him
    '''
    pass


class NotEnoughSpaceException(Exception):
    '''
    Exception raised when there is not enough space for the new upload
    '''
    pass


class UploadNotExistingException(Exception):
    '''
    Exception raised when we try to access a non existing upload
    '''
    pass


class UserNotActivatedException(Exception):
    '''
    Exception raised when trying to reach a non existing user
    '''
    pass


class SnapshotNotExistingException(Exception):
    '''
    Exception raised when trying to reach a non existing snapshot
    '''
    pass


class ValidationError(ValueError):
    pass


class ComputationalModuleError(ValueError):
    pass




