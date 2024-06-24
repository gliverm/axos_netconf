"""
Basic wrapper around SMx Rest API calls.

Notes: 
SMx supports GET, PUT, POST, DELETE
PUT to modify existing resource - do no know if it acts like a PATCH or total replacement
Pagination do not see max limit in swagger - not sure how SMX gets count of total records
Offset/limit appears to be consistent across commands
authorization base64 WWW-Authentication in HTTP header
Status codes: 
    200,201 - ok
    400 - Bad Request
    401 - Unauthorized
    403 - Forbidden
    404 - Not found
    422 - Unproccessable Entity
    500 - Internal Server Error
Use HTTPS
Service relationship: subscriber -> ONT -> Service -> Service Template -> Policy-Map -> Class-Map
Before service template build class-map per service tier and policy map per service tier

Design Choices:

"""

from app.lib.smx.session import SmxRestSessionMixin
from app.lib.smx.session import SmxConfigMixin
from app.lib.smx.session import SmxFaultMixin


# Session class listed as last mixin
class NetconfSession(SmxConfigMixin, SmxFaultMixin, SmxRestSessionMixin):
    pass
