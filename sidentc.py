#!/usr/bin/env python3
import socket
import argparse

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("--ident_ip")
parser.add_argument("--ident_port", default = 113, type = int)
parser.add_argument("--server_port", required = True, type = int)
parser.add_argument("--client_port", required = True, type = int)
args = parser.parse_args()

# Create a socket.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
sock.connect((args.ident_ip, args.ident_port))

# Make a query.
sock.send("{},{}".format(args.server_port, args.client_port).encode())

# Get the data and print it to stdout.
print(sock.recv(4096))
