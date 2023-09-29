#  coding: utf-8 
import socketserver
import os
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

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
 
        print(path)
            # Read the contents of the HTML file
        if method in "POST/PUT/DELETE":
            error_response = b"HTTP/1.1 405 Method Not Allowed \r\n\r\nFile Not Found"
            self.request.sendall(error_response)
        else:
            try:
                if os.path.isdir(path):
                    # Raise an exception for directory requests
                    raise IsADirectoryError

                with open(path, "rb") as file:
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
                    redirect_url = path+"/"
                    print(redirect_url)
                    error_response = (
                        b"HTTP/1.1 301 Found\r\n"
                        b"Location: " + redirect_url.encode() + b"\r\n"
                        b"\r\n"
                    )       
                    self.request.sendall(error_response)         
                else :
                    error_response = b"HTTP/1.1 200 ok\r\n\r\n you are requesting a folder"
                    self.request.sendall(error_response)


        
            print ("Got a request of: %s\n" % self.data)
            #self.request.sendall(bytearray("OK",'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()