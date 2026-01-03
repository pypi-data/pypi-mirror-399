from enum import Enum
from typing import final


# Http status codes
# Following RFC 9110 https://datatracker.ietf.org/doc/html/rfc9110


class HttpStatusGroup(Enum):
    INFORMATIONAL = 1
    SUCCESSFUL = 2
    REDIRECTION = 3
    CLIENT_ERROR = 4
    SERVER_ERROR = 5


class HttpStatus(int, Enum):
    # 1xx Informational
    HTTP_100_CONTINUE = (100, HttpStatusGroup.INFORMATIONAL, "Continue")
    HTTP_101_SWITCHING_PROTOCOLS = (
        101,
        HttpStatusGroup.INFORMATIONAL,
        "Switching Protocols",
    )
    HTTP_102_PROCESSING = (
        102,
        HttpStatusGroup.INFORMATIONAL,
        "Processing",
    )  # Deprecated
    HTTP_103_PROCESSING = (103, HttpStatusGroup.INFORMATIONAL, "Early Hints")

    # 2xx Success
    HTTP_200_OK = (200, HttpStatusGroup.SUCCESSFUL, "OK")
    HTTP_201_CREATED = (201, HttpStatusGroup.SUCCESSFUL, "Created")
    HTTP_202_ACCEPTED = (202, HttpStatusGroup.SUCCESSFUL, "Accepted")
    HTTP_203_NON_AUTHORITATIVE_INFORMATION = (
        203,
        HttpStatusGroup.SUCCESSFUL,
        "Non-Authoritative Information",
    )
    HTTP_204_NO_CONTENT = (204, HttpStatusGroup.SUCCESSFUL, "No Content")
    HTTP_205_RESET_CONTENT = (205, HttpStatusGroup.SUCCESSFUL, "Reset Content")
    HTTP_206_PARTIAL_CONTENT = (206, HttpStatusGroup.SUCCESSFUL, "Partial Content")
    HTTP_207_MULTI_STATUS = (207, HttpStatusGroup.SUCCESSFUL, "Multi-Status")
    HTTP_208_ALREADY_REPORTED = (208, HttpStatusGroup.SUCCESSFUL, "Already Reported")
    HTTP_226_IM_USED = (226, HttpStatusGroup.SUCCESSFUL, "IM Used")

    # 3xx Redirection
    HTTP_300_MULTIPLE_CHOICES = (300, HttpStatusGroup.REDIRECTION, "Multiple Choices")
    HTTP_301_MOVED_PERMANENTLY = (301, HttpStatusGroup.REDIRECTION, "Moved Permanently")
    HTTP_302_FOUND = (302, HttpStatusGroup.REDIRECTION, "Found")
    HTTP_303_SEE_OTHER = (303, HttpStatusGroup.REDIRECTION, "See Other")
    HTTP_304_NOT_MODIFIED = (304, HttpStatusGroup.REDIRECTION, "Not Modified")
    HTTP_305_USE_PROXY = (305, HttpStatusGroup.REDIRECTION, "Use Proxy")
    HTTP_306_RESERVED = (306, HttpStatusGroup.REDIRECTION, "Reserved")
    HTTP_307_TEMPORARY_REDIRECT = (
        307,
        HttpStatusGroup.REDIRECTION,
        "Temporary Redirect",
    )
    HTTP_308_PERMANENT_REDIRECT = (
        308,
        HttpStatusGroup.REDIRECTION,
        "Permanent Redirect",
    )

    # 4xx Client Error
    HTTP_400_BAD_REQUEST = (400, HttpStatusGroup.CLIENT_ERROR, "Bad Request")
    HTTP_401_UNAUTHORIZED = (401, HttpStatusGroup.CLIENT_ERROR, "Unauthorized")
    HTTP_402_PAYMENT_REQUIRED = (402, HttpStatusGroup.CLIENT_ERROR, "Payment Required")
    HTTP_403_FORBIDDEN = (403, HttpStatusGroup.CLIENT_ERROR, "Forbidden")
    HTTP_404_NOT_FOUND = (404, HttpStatusGroup.CLIENT_ERROR, "Not Found")
    HTTP_405_METHOD_NOT_ALLOWED = (
        405,
        HttpStatusGroup.CLIENT_ERROR,
        "Method Not Allowed",
    )
    HTTP_406_NOT_ACCEPTABLE = (406, HttpStatusGroup.CLIENT_ERROR, "Not Acceptable")
    HTTP_407_PROXY_AUTHENTICATION_REQUIRED = (
        407,
        HttpStatusGroup.CLIENT_ERROR,
        "Proxy Authentication Required",
    )
    HTTP_408_REQUEST_TIMEOUT = (408, HttpStatusGroup.CLIENT_ERROR, "Request Timeout")
    HTTP_409_CONFLICT = (409, HttpStatusGroup.CLIENT_ERROR, "Conflict")
    HTTP_410_GONE = (410, HttpStatusGroup.CLIENT_ERROR, "Gone")
    HTTP_411_LENGTH_REQUIRED = (411, HttpStatusGroup.CLIENT_ERROR, "Length Required")
    HTTP_412_PRECONDITION_FAILED = (
        412,
        HttpStatusGroup.CLIENT_ERROR,
        "Precondition Failed",
    )
    HTTP_413_CONTENT_TOO_LARGE = (
        413,
        HttpStatusGroup.CLIENT_ERROR,
        "Content Too Large",
    )
    HTTP_414_URI_TOO_LONG = (414, HttpStatusGroup.CLIENT_ERROR, "URI Too Long")
    HTTP_415_UNSUPPORTED_MEDIA_TYPE = (
        415,
        HttpStatusGroup.CLIENT_ERROR,
        "Unsupported Media Type",
    )
    HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE = (
        416,
        HttpStatusGroup.CLIENT_ERROR,
        "Requested range not satisfiable",
    )
    HTTP_417_EXPECTATION_FAILED = (
        417,
        HttpStatusGroup.CLIENT_ERROR,
        "Expectation Failed",
    )
    HTTP_418_I_AM_A_TEAPOT = (
        418,
        HttpStatusGroup.CLIENT_ERROR,
        "I'm a teapot",
    )  # Deprecated
    HTTP_421_MISDIRECTED_REQUEST = (
        421,
        HttpStatusGroup.CLIENT_ERROR,
        "Misdirected Request",
    )
    HTTP_422_UNPROCESSABLE_CONTENT = (
        422,
        HttpStatusGroup.CLIENT_ERROR,
        "Unprocessable Content",
    )
    HTTP_423_LOCKED = (423, HttpStatusGroup.CLIENT_ERROR, "Locked")
    HTTP_424_FAILED_DEPENDENCY = (
        424,
        HttpStatusGroup.CLIENT_ERROR,
        "Failed Dependency",
    )
    HTTP_425_TOO_EARLY = (425, HttpStatusGroup.CLIENT_ERROR, "Too Early")
    HTTP_426_UPGRADE_REQUIRED = (426, HttpStatusGroup.CLIENT_ERROR, "Upgrade Required")
    HTTP_428_PRECONDITION_REQUIRED = (
        428,
        HttpStatusGroup.CLIENT_ERROR,
        "Precondition Required",
    )
    HTTP_429_TOO_MANY_REQUESTS = (
        429,
        HttpStatusGroup.CLIENT_ERROR,
        "Too Many Requests",
    )
    HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE = (
        431,
        HttpStatusGroup.CLIENT_ERROR,
        "Request Header Fields Too Large",
    )
    HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS = (
        451,
        HttpStatusGroup.CLIENT_ERROR,
        "Unavailable For Legal Reasons",
    )

    # 5xx Server Errors
    HTTP_500_INTERNAL_SERVER_ERROR = (
        500,
        HttpStatusGroup.SERVER_ERROR,
        "Internal Server Error",
    )
    HTTP_501_NOT_IMPLEMENTED = (501, HttpStatusGroup.SERVER_ERROR, "Not Implemented")
    HTTP_502_BAD_GATEWAY = (502, HttpStatusGroup.SERVER_ERROR, "Bad Gateway")
    HTTP_503_SERVICE_UNAVAILABLE = (
        503,
        HttpStatusGroup.SERVER_ERROR,
        "Service Unavailable",
    )
    HTTP_504_GATEWAY_TIMEOUT = (504, HttpStatusGroup.SERVER_ERROR, "Gateway Timeout")
    HTTP_505_HTTP_VERSION_NOT_SUPPORTED = (
        505,
        HttpStatusGroup.SERVER_ERROR,
        "HTTP Version not supported",
    )
    HTTP_506_VARIANT_ALSO_NEGOTIATES = (
        506,
        HttpStatusGroup.SERVER_ERROR,
        "Variant Also Negotiates",
    )
    HTTP_507_INSUFFICIENT_STORAGE = (
        507,
        HttpStatusGroup.SERVER_ERROR,
        "Insufficient Storage",
    )
    HTTP_508_LOOP_DETECTED = (508, HttpStatusGroup.SERVER_ERROR, "Loop Detected")
    HTTP_511_NETWORK_AUTHENTICATION_REQUIRED = (
        511,
        HttpStatusGroup.SERVER_ERROR,
        "Network Authentication Required",
    )

    @property
    def is_1xx_informational(self) -> bool:
        return self.group == HttpStatusGroup.INFORMATIONAL

    @property
    def is_2xx_successful(self) -> bool:
        return self.group == HttpStatusGroup.SUCCESSFUL

    @property
    def is_3xx_redirection(self) -> bool:
        return self.group == HttpStatusGroup.REDIRECTION

    @property
    def is_4xx_client_error(self) -> bool:
        return self.group == HttpStatusGroup.CLIENT_ERROR

    @property
    def is_5xx_server_error(self) -> bool:
        return self.group == HttpStatusGroup.SERVER_ERROR

    @property
    def is_error(self) -> bool:
        """
        Determines if the status code is an error.
        Returns True if it is a 4xx Client Error or a 5xx Server Error.
        """
        return self.is_4xx_client_error or self.is_5xx_server_error

    code: int
    group: HttpStatusGroup
    description: str

    def __new__(cls, code: int, group: HttpStatusGroup, description: str):
        obj = int.__new__(cls, code)
        obj._value_ = code
        obj.code = code
        obj.group = group
        obj.description = description
        return obj

    def __str__(self) -> str:
        return str(self.code)

    def __repr__(self) -> str:
        return f"<HttpStatus {self.code} {self.description!r}>"


@final
class HttpMethod(str, Enum):
    """
    An enum mapping all standard HTTP methods.
    """

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"

    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"
    CONNECT = "CONNECT"

    @classmethod
    def all_methods(cls) -> list[str]:
        """Returns a list of all defined method names as uppercase strings."""
        return [member.value for member in cls]

    @classmethod
    def is_valid(cls, method_name: str) -> bool:
        """Checks if a given string is a valid HTTP method."""
        return method_name.upper() in cls.all_methods()


# MediaType
class MediaType(str, Enum):
    ALL = "*/*"
    APPLICATION_ATOM_XML = "application/atom+xml"
    APPLICATION_CBOR = "application/cbor"
    APPLICATION_FORM_URLENCODED = "application/x-www-form-urlencoded"
    APPLICATION_GRAPHQL_RESPONSE = "application/graphql-response+json"
    APPLICATION_JSON = "application/json"
    APPLICATION_NDJSON = "application/x-ndjson"
    APPLICATION_OCTET_STREAM = "application/octet-stream"
    APPLICATION_PDF = "application/pdf"
    APPLICATION_PROBLEM_JSON = "application/problem+json"
    APPLICATION_PROBLEM_XML = "application/problem+xml"
    APPLICATION_PROTOBUF = "application/x-protobuf"
    APPLICATION_RSS_XML = "application/rss+xml"
    APPLICATION_XHTML_XML = "application/xhtml+xml"
    APPLICATION_XML = "application/xml"
    APPLICATION_YAML = "application/yaml"
    IMAGE_GIF = "image/gif"
    IMAGE_JPEG = "image/jpeg"
    IMAGE_PNG = "image/png"
    MULTIPART_FORM_DATA = "multipart/form-data"
    MULTIPART_MIXED = "multipart/mixed"
    MULTIPART_RELATED = "multipart/related"
    TEXT_EVENT_STREAM = "text/event-stream"
    TEXT_HTML = "text/html"
    TEXT_MARKDOWN = "text/markdown"
    TEXT_PLAIN = "text/plain"
    TEXT_XML = "text/xml"

    @property
    def type(self) -> str:
        return self.value.split("/")[0]

    @property
    def subtype(self) -> str:
        return self.value.split("/")[1]

    @classmethod
    def value_of(cls, value: str) -> "MediaType | None":
        for member in cls:
            if member.value == value.lower():
                return member
        return None

    # Helper method to set media type with charset
    @classmethod
    def with_charset(cls, media_type: "MediaType", charset: str = "UTF-8") -> str:
        return f"{media_type.value}; charset={charset}"

    def __str__(self) -> str:
        return self.value
