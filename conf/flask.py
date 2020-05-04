#ENV
#What environment the app is running in. Flask and extensions may enable behaviors based on the environment, such as enabling debug mode.
#The env attribute maps to this config key. This is set by the FLASK_ENV environment variable and may not behave as expected if set in code.
#Do not enable development when deploying in production.
#Default: 'production'

DEBUG = True
#exceptions, and the server will be reloaded when code changes. The debug attribute maps to this config key.
#This is enabled when ENV is 'development' and is overridden by the FLASK_DEBUG environment variable. It may not behave as expected if set in code.
#Do not enable debug mode when deploying in production.
#Default: True if ENV is 'development', or False otherwise.

#TESTING
#Enable testing mode. Exceptions are propagated rather than handled by the the app’s error handlers.
#Extensions may also change their behavior to facilitate easier testing. You should enable this in your own tests.
#Default: False

#PROPAGATE_EXCEPTIONS
#Exceptions are re-raised rather than being handled by the app’s error handlers. If not set, this is implicitly true if TESTING or DEBUG is enabled.
#Default: None

#PRESERVE_CONTEXT_ON_EXCEPTION
#Don’t pop the request context when an exception occurs. If not set, this is true if DEBUG is true.
#This allows debuggers to introspect the request data on errors, and should normally not need to be set directly.
#Default: None

#TRAP_HTTP_EXCEPTIONS
#If there is no handler for an HTTPException-type exception, re-raise it to be handled by the interactive debugger instead of returning it as
#a simple error response.
#Default: False

#TRAP_BAD_REQUEST_ERRORS
#Trying to access a key that doesn’t exist from request dicts like args and form will return a 400 Bad Request error page.
#Enable this to treat the error as an unhandled exception instead so that you get the interactive debugger.
#This is a more specific version of TRAP_HTTP_EXCEPTIONS. If unset, it is enabled in debug mode.
#Default: None

SECRET_KEY = 'x3JGW2gQLZgGYSJPoCwwiQDXB8r5TAro'
#A secret key that will be used for securely signing the session cookie and can be used for any other security related needs by extensions or
#your application. It should be a long random string of bytes, although unicode is accepted too. For example, copy the output of this to your
#config:
#https://randomkeygen.com/
#$ python -c 'import os; print(os.urandom(16))'
#b'_5#y2L"F4Q8z\n\xec]/'
#Do not reveal the secret key when posting questions or committing code.
#Default: None

#SESSION_COOKIE_NAME
#The name of the session cookie. Can be changed in case you already have a cookie with the same name.
#Default: 'session'

#SESSION_COOKIE_DOMAIN
#The domain match rule that the session cookie will be valid for. If not set, the cookie will be valid for all subdomains of SERVER_NAME.
#If False, the cookie’s domain will not be set.
#Default: None

#SESSION_COOKIE_PATH
#The path that the session cookie will be valid for. If not set, the cookie will be valid underneath APPLICATION_ROOT or / if that is not set.
#Default: None

#SESSION_COOKIE_HTTPONLY
#Browsers will not allow JavaScript access to cookies marked as “HTTP only” for security.
#Default: True

#SESSION_COOKIE_SECURE
#Browsers will only send cookies with requests over HTTPS if the cookie is marked “secure”. The application must be served over HTTPS for
#this to make sense.
#Default: False

#SESSION_COOKIE_SAMESITE
#Restrict how cookies are sent with requests from external sites. Can be set to 'Lax' (recommended) or 'Strict'. See Set-Cookie options.
#Default: None

#PERMANENT_SESSION_LIFETIME
#If session.permanent is true, the cookie’s expiration will be set this number of seconds in the future.
#Can either be a datetime.timedelta or an int.
#Flask’s default cookie implementation validates that the cryptographic signature is not older than this value.
#Default: timedelta(days=31) (2678400 seconds)

#SESSION_REFRESH_EACH_REQUEST
#Control whether the cookie is sent with every response when session.permanent is true. Sending the cookie every time (the default) can more
#reliably keep the session from expiring, but uses more bandwidth. Non-permanent sessions are not affected.
#Default: True

#USE_X_SENDFILE
#When serving files, set the X-Sendfile header instead of serving the data with Flask. Some web servers, such as Apache, recognize this and serve
#the data more efficiently. This only makes sense when using such a server.
#Default: False

#SEND_FILE_MAX_AGE_DEFAULT
#When serving files, set the cache control max age to this number of seconds. Can either be a datetime.timedelta or an int. Override this value on
#a per-file basis using get_send_file_max_age() on the application or blueprint.
#Default: timedelta(hours=12) (43200 seconds)

#SERVER_NAME
#Inform the application what host and port it is bound to. Required for subdomain route matching support.
#If set, will be used for the session cookie domain if SESSION_COOKIE_DOMAIN is not set. Modern web browsers will not allow setting cookies for
#domains without a dot. To use a domain locally, add any names that should route to the app to your hosts file.
#127.0.0.1 localhost.dev
#If set, url_for can generate external URLs with only an application context instead of a request context.
#Default: None

#APPLICATION_ROOT
#Inform the application what path it is mounted under by the application / web server. This is used for generating URLs outside the context of a
#request (inside a request, the dispatcher is responsible for setting SCRIPT_NAME instead; see Application Dispatching for examples of dispatch
#configuration).
#Will be used for the session cookie path if SESSION_COOKIE_PATH is not set.
#Default: '/'

#PREFERRED_URL_SCHEME
#Use this scheme for generating external URLs when not in a request context.
#Default: 'http'

#MAX_CONTENT_LENGTH
#Don’t read more than this many bytes from the incoming request data. If not set and the request does not specify a CONTENT_LENGTH, no data will
#be read for security.
#Default: None

#JSON_AS_ASCII
#Serialize objects to ASCII-encoded JSON. If this is disabled, the JSON will be returned as a Unicode string, or encoded as UTF-8 by jsonify.
#This has security implications when rendering the JSON into JavaScript in templates, and should typically remain enabled.
#Default: True

#JSON_SORT_KEYS
#Sort the keys of JSON objects alphabetically. This is useful for caching because it ensures the data is serialized the same way no matter what
#Python’s hash seed is. While not recommended, you can disable this for a possible performance improvement at the cost of caching.
#Default: True

#JSONIFY_PRETTYPRINT_REGULAR
#jsonify responses will be output with newlines, spaces, and indentation for easier reading by humans. Always enabled in debug mode.
#Default: False

#JSONIFY_MIMETYPE
#The mimetype of jsonify responses.
#Default: 'application/json'

#TEMPLATES_AUTO_RELOAD
#Reload templates when they are changed. If not set, it will be enabled in debug mode.
#Default: None

#EXPLAIN_TEMPLATE_LOADING
#Log debugging information tracing how a template file was loaded. This can be useful to figure out why a template was not loaded or the wrong
#file appears to be loaded.
#Default: False

#MAX_COOKIE_SIZE
#Warn if cookie headers are larger than this many bytes. Defaults to 4093. Larger cookies may be silently ignored by browsers. Set to 0 to disable
#the warning.
