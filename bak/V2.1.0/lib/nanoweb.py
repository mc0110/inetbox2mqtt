import uasyncio as asyncio
import uerrno


class HttpError(Exception):
    pass


class Request:
    url = ""
    method = ""
    headers = {}
    route = ""
    read = None
    write = None
    close = None
    args = None
    param = None
    

    def __init__(self):
        self.url = ""
        self.method = ""
        self.headers = {}
        self.route = ""
        self.read = None
        self.write = None
        self.close = None


async def write(request, data):
    await request.write(
        data.encode('ISO-8859-1') if type(data) == str else data
    )


async def error(request, code, reason):
    await request.write("HTTP/1.1 %s %s\r\n\r\n" % (code, reason))
    await request.write("<h1>%s</h1>" % (reason))


async def send_file(request, filename, segment=64, binary=False):
    #print("send_file:", filename, segment, binary)      
    try:
       with open(filename, 'rb' if binary else 'r') as f:
            while True:
                data = f.read(segment)
                if not data:
                    break
                await request.write(data)
    except OSError as e:
        if e.args[0] != uerrno.ENOENT:
            raise
        raise HttpError(request, 404, "File Not Found")


class Nanoweb:

    extract_headers = ('Authorization', 'Content-Length', 'Content-Type', 'Content-Disposition', 'User-Agent')
    headers = {}

    routes = {}
    assets_extensions = ('html', 'css', 'js')

    callback_request = None
    callback_error = staticmethod(error)

    STATIC_DIR = '/'
    INDEX_FILE = STATIC_DIR + 'index.html'
    debug = False

    def __init__(self, port=80, address='0.0.0.0', debug=False, dir='/'):
        self.port = port
        self.address = address
        self.debug = debug
        self.STATIC_DIR = dir

    def route(self, route):
        """Route decorator"""
        def decorator(func):
            self.routes[route] = func
            return func
        return decorator

    async def generate_output(self, request, handler):
        """Generate output from handler

        `handler` can be :
         * dict representing the template context
         * string, considered as a path to a file
         * tuple where the first item is filename and the second
           is the template context
         * callable, the output of which is sent to the client
        """
        while True:
            if self.debug: print("handler: ", type(handler))
            if isinstance(handler, dict):
                if self.debug: print("DICT-Handler: ", request.url, str(handler))
                handler = (request.url, handler)

            if isinstance(handler, str):
                await write(request, "HTTP/1.1 200 OK\r\n\r\n")
                await send_file(request, handler)
            elif isinstance(handler, tuple):
                await write(request, "HTTP/1.1 200 OK\r\n\r\n")
                filename, context = handler
                context = context() if callable(context) else context
                try:
                    with open(filename, "r") as f:
                        for l in f:
                            await write(request, l.format(**context))
                except OSError as e:
                    if e.args[0] != uerrno.ENOENT:
                        raise
                    raise HttpError(request, 404, "File Not Found")
            else:
                handler = await handler(request)
                if handler:
                    # handler can returns data that can be fed back
                    # to the input of the function
                    continue
            break

    async def handle(self, reader, writer):
        items = await reader.readline()
        items = items.decode('ascii').split()
        if len(items) != 3:
            return

        request = Request()
        request.read = reader.read
        request.write = writer.awrite
        request.close = writer.aclose
        
        request.method, request.url, version = items
        
        if self.debug: print("Method: ", request.method)
        if self.debug: print("URL: ",request.url)
        if self.debug: print("Version: ",version)
        if request.url.find("?") > -1:
            request.url, a = request.url.split("?")
            if a != "":
                if self.debug: print("PARAM:", a)
                request.param = {}
                a = a.split("&")
                for i in a:
                    if self.debug: print(i)
                    q = i.split("=", 1)
                    if self.debug: print(q)
                    request.param.update({q[0]: q[1].replace('%2F','/')})


        try:
            try:
                if version not in ("HTTP/1.0", "HTTP/1.1"):
                    raise HttpError(request, 505, "Version Not Supported")

                while True:
                    items = await reader.readline()
                    items = items.decode('ascii').split(":", 1)
                    if len(items) == 2:
                        header, value = items
                        value = value.strip()

                        if header in self.extract_headers:
                            request.headers[header] = value
                    elif len(items) == 1:
                        break
                    
                if self.debug: print("Header: ", request.headers)
                if request.method == 'POST' and request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
                        b = int(request.headers['Content-Length'])
                        a = await request.read(b)
                        print(a)
                        a = a.decode('ascii').split("&")
                        if self.debug: print("POST-Section: args: ", a)
                        request.args = {}
                        for i in a:
                            q = i.split("=", 1)
                            request.args.update({q[0]: q[1]})
                        if self.debug: print("POST: ", request.args)

                if self.callback_request:
                    self.callback_request(request)
                
                if self.debug: print("WorkingURL: ", request.url)
                if request.url in self.routes:
                    # 1. If current url exists in routes
                    if self.debug: print("1. URL in routes: "+request.url)
                    request.route = request.url
                    await self.generate_output(request,
                                               self.routes[request.url])
                else:
                    # 2. Search url in routes with wildcard
                    for route, handler in self.routes.items():
                        # print(route, handler)
                        if route == request.url \
                            or (route[-1] == '*' and
                                request.url.startswith(route[:-1])):
                            if self.debug: print("2. URL ww: "+request.url)
                            request.route = route
                            await self.generate_output(request, handler)
                            break
                    else:
                        # 3. Try to load index file
                        if request.url in ('', '/'):
                            if self.debug: print("3. Indexfile: "+request.url)
                            await send_file(request, self.INDEX_FILE)
                        else:
                            if self.debug: print("4. Step: "+request.url)
                            # 4. Current url have an assets extension ?
                            for extension in self.assets_extensions:
                                if request.url.endswith('.' + extension):
                                    await send_file(
                                        request,
                                        '%s%s' % (
                                            self.STATIC_DIR,
                                            request.url,
                                        ),
                                        binary=True,
                                    )
                                    break
                            else:
                                raise HttpError(request, 404, "File Not Found")
            except HttpError as e:
                request, code, message = e.args
                await self.callback_error(request, code, message)
        except OSError as e:
            # Skip ECONNRESET error (client abort request)
            if e.args[0] != uerrno.ECONNRESET:
                raise
        finally:
            await writer.aclose()

    async def run(self):
        return await asyncio.start_server(self.handle, self.address, self.port)
