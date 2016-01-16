import webapp2

import ReSTify


application = webapp2.WSGIApplication(
    [
        ('/.*', ReSTify.ReST),
       ],
    debug=True)