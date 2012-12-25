# coding: utf-8

import re
import hashlib

from pyramid.security import unauthenticated_userid
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from pyramid.view import forbidden_view_config

from pysite.usrmgr.const import *
from pysite.exc import PySiteError


class AuthProviderFactory(object):
    @staticmethod
    def factory(type_):
        if type_ == 'sqlalchemy':
            from pysite.usrmgr.models import Principal
            return Principal()
        raise Exception("Unknown auth provider: '{0}'".format(type_))


class User(object):

    def __init__(self, request):
        self._request = request
        self._metadata = None
        self.uid = None
        self.principal = None
        self.roles = None
        self.init_nobody()
        self.auth_provider = AuthProviderFactory.factory(
            request.registry.settings['auth.provider'])

    def load_by_principal(self, principal):
        p = self.auth_provider.load_by_principal(principal)
        self.init_from_principal(p)

    def init_nobody(self):
        self.uid = NOBODY_UID
        self.principal = NOBODY_PRINCIPAL
        self._metadata = dict(
            email        = NOBODY_EMAIL,
            display_name = NOBODY_DISPLAY_NAME
        )
        self.roles = None

    def init_from_principal(self, p):
        """Initialises authenticated user.
        """
        self.uid                       = p.id
        self.principal                 = p.principal
        # Must copy roles, loaded principal will go out of scope!
        self.roles                     = [r for r in p.role_names]
        self._metadata['email']        = p.email
        self._metadata['first_name']   = p.first_name
        self._metadata['last_name']    = p.last_name
        self._metadata['display_name'] = p.display_name

    def is_auth(self):
        """Tells whether user is authenticated, i.e. is not nobody
        """
        return self.uid != NOBODY_UID

    def login(self, login, pwd):
        """Login by principal/email and password
           
           Return True on success, else False
        """
        if '@' in login:
            try:
                p = self.auth_provider.login_by_email(email=login, pwd=pwd)
            except LookupError:
                # TODO Log exception
                return False
        else:
            try:
                p = self.auth_provider.login_by_principal(
                    principal=login, pwd=pwd)
            except LookupError:
                # TODO Log exception
                return False
        self.init_from_principal(p)
        self._request.session.new_csrf_token()
        return True

    def logout(self):
        """Logout, resets metadata back to nobody
        """
        self.auth_provider.logout(self.uid)
        self.init_nobody()
        self._request.session.new_csrf_token()

    def __getattr__(self, name):
        try:
            return self._metadata[name]
        except KeyError:
            raise AttributeError("Attribute '{0}' not found".format(name))


def group_finder(userid, request):
    """Returns roles of the currently logged in user
       
    Role names are prefixed with 'r:'.
    Nobody has no roles.
    Param 'userid' must match principal of current user, else throws error
    """
    usr = request.user
    # unauthenticated_userid becomes authenticated_userid if groupfinder
    # returns not None.
    if userid != usr.principal:
        # This should not happen (tm)
        raise Exception("Userid '{0}' does not match current user.principal '{1}'".format(
            userid, usr.principal))
    if usr.uid == NOBODY_UID:
        gr = []
    roles = usr.roles
    if not roles:
        gr = []
    else:
        gr = [ 'r:'+r for r in roles ]
    return gr


def get_user(request):
    principal = unauthenticated_userid(request)
    usr = User(request)
    if principal is not None:
        usr.load_by_principal(principal)
    return usr


@forbidden_view_config(xhr=False)
def forbidden_view(request):
    if request.user.is_auth():
        html = """<html>
            <head>
              <title>403 Forbidden</title>
            </head>
            <body>
              <h1>403 Forbidden</h1>
              <p>You are not allowed to access this resource.</p>
              <p>{0}</p>
             </body>
            </html>
        """.format(request.exception.message)
        return Response(html)
    else:
        request.session.flash(request.url, queue='login_referrer')
        return HTTPFound(location=request.resource_url(
            request.context, '@@login'),)


# https://github.com/django/django/blob/master/django/contrib/auth/hashers.py
def encrypt_pwd(pwd, salt=None, scheme='PLAIN-MD5'):
    scheme = scheme.upper()
    try:
        pwd = pwd.encode('utf-8')
    except AttributeError:
        pass # Already was byte string
    if scheme == 'PLAIN':
        salt = b''
        hash = pwd
    elif scheme == 'PLAIN-MD5':
        salt = b''
        hash = hashlib.md5(pwd).hexdigest()
    else:
        raise PySiteError("Unsupported encryption scheme: '{0}'".format(
            scheme))
    try:
        scheme = scheme.encode('utf-8')
    except AttributeError:
        pass # Already was byte string
    return (b'{' + scheme + b'}' + hash + salt).decode('utf-8')


def check_pwd(pwd, enc_pwd, scheme='PLAIN-MD5'):
    scheme = scheme.upper()
    m = re.match(r'(\{'+scheme+'\})(.+)', enc_pwd)
    if m:
        scheme = m.group(1)
        pwd = m.group(2)
    else:
        raise PySiteError(
            "Invalid enc_pwd format. Should be '{SCHEME}HEX_OR_BASE64'.")
    if scheme == 'PLAIN':
        salt = b''
    elif scheme == 'PLAIN-MD5':
        salt = b''
    else:
        raise PySiteError("Unsupported encryption scheme: '{0}'".format(
            scheme))
    pwd_enc = encrypt_pwd(pwd, salt, scheme)
    return (pwd_enc == enc_pwd)
