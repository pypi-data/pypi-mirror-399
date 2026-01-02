from typing import Literal, Union, List

HTTP_METHODS = Literal['GET', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE', 'TRACE', 'CONNECT', 'OPTION',]

HTTP_METHODS_ARGS_TYPE = Union[HTTP_METHODS, List[HTTP_METHODS]]
