# Name or identifier: Ba Thien Huynh
# License: MIT License



# MIT License

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE
import socketserver
import os
def extract_path(request_data):
    request_data = request_data.decode('utf-8')
    request_lines = request_data.split("\r\n")
    if len(request_lines) > 0:
        first_line = request_lines[0]
        parts = first_line.split(" ")
        if len(parts) >= 2:
            http_method = parts[0]
            requested_path = parts[1]

            # Now, 'requested_path' contains the path the client is requesting
            #print("HTTP Method:", http_method)
            #print("Requested Path:", requested_path)
            return http_method,requested_path
    else:
        print("Invalid HTTP request")



def get_contenttype(path):
    if ".css" in path:
        content_type = "text/css"
    elif ".html" in path:
        content_type = "text/html"
    else:
        content_type = "application/octet-stream"  # Default for unknown types
    return content_type
class MyWebServer(socketserver.BaseRequestHandler):        
    def handle(self):
        self.data = self.request.recv(1024).strip()

        method,request_path=extract_path(self.data)
        content_type=get_contenttype(request_path)

        path=os.path.normpath(os.getcwd()+"/www")
        path=path+request_path
            # Read the contents of the HTML file
        if method in "POST/PUT/DELETE":
            error_response = b"HTTP/1.1 405 Method Not Allowed \r\n\r\nFile Not Found"
            self.request.sendall(error_response)
        else:
            try:
                if os.path.isdir(path):
                    # Raise an exception for directory requests
                    raise IsADirectoryError

                with open(path.replace("/..",""), "rb") as file:
                    file_content = file.read()
                response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Length: " + str(len(file_content)).encode() + b"\r\n"
                b"Content-Type: " + content_type.encode() + b"\r\n"
                b"\r\n" + file_content
                )
                self.request.sendall(response)              
                
            except FileNotFoundError:
                # Handle the case when the file is not found
                error_response = b"HTTP/1.1 404 Not Found\r\n\r\nFile Not Found"
                self.request.sendall(error_response)

            except IsADirectoryError:
                # Handle the case when the path is a directory
                # print("request folder "+ path)
                #print(path[-1].isalpha())
                if  path[-1].isalpha():
                    parts = path.split("/")
                    ans=parts[-1]
                    # Get the substring after the last "/"
                    redirect_url = "/"+ans+"/"
                    error_response = (
                        b"HTTP/1.1 301 Found\r\n"
                        #b"Content-Length: " + str(len(file_content)).encode() + b"\r\n"
                        b"Location: " + redirect_url.encode('utf-8') + b"\r\n"
                        #b"Content-Type: text/html \r\n"
                        b"\r\n"#+file_content
                    )       
                    self.request.sendall(error_response)         
                else :
                    path=path+"index.html"
                    with open(path.replace("/..",""), "rb") as file:
                        file_content = file.read()
                    
                    response = (b"HTTP/1.1 200 OK\r\n"        
                                b"Content-Length: " + str(len(file_content)).encode() + b"\r\n"
                                b"Content-Type:  text/html\r\n"
                                b"\r\n" + file_content)
                    self.request.sendall(response)


        
            #print ("Got a request of: %s\n" % self.data)
            #self.request.sendall(bytearray("OK",'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
