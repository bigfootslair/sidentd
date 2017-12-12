#!/usr/bin/env python3
import socket
import argparse
import multiprocessing
import uuid

# Set the version.
__version__ = "0.0.3"

# Parse arguments.
parser = argparse.ArgumentParser(description = "A simple ident daemon written in python")
parser.add_argument("--bind_ip", help = "Bind to this IP", default = "0.0.0.0")
parser.add_argument("--bind_port", help = "Bind to this port", default = 113, type = int)
parser.add_argument("--port", help = "Only respond to queries for this port", required = False, type = int)
parser.add_argument("--connection_limit", help = "The maximum connections allowed at a time", default = 0, type = int)
parser.add_argument("--file", help = "If set reads the ident from a file")
parser.add_argument("--random", help = "If set gives a random ident", action = "store_true")
parser.add_argument("--static", help = "If set always give this ident")
parser.add_argument("--error", help = "If set always respond with an unknown user error", action = "store_true")
parser.add_argument("--version", action = 'version', version = "sidentd " + __version__)
args = parser.parse_args()

# Make a socket.
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set the REUSEADD property on it.
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind to the IP and port given.
server.bind((args.bind_ip, args.bind_port))

# Start listening for connections.
server.listen(args.connection_limit)

# Function that handles connections.
def handle_connection(connection, address):
	print("DEBUG: Connection handler starting...")

	# Get a query.
	data = connection.recv(4096).decode()

	# Parse the query.
	try:
		server_port, client_port = data.split(",")
	except:
		print("ERROR: We got an invalid port!")
		return

	# If we aren't suppose to respond on this port, respond with a NO-USER error.
	if args.port and not int(client_port) == args.port:
		print("ERROR: We got a port that doesn't match --port.")
		connection.send("{}, {} : ERROR : NO-USER".format(server_port, client_port).encode())
		return

	# Send an ident.
	if args.file:
		# Read the ident from the file.
		try:
			with open(args.file, "r") as file:
				file_string = file.readline().split("\n")[0]
		except:
			# If we have any errors reading the file, respond with an UNKNOWN-ERROR error.
			connection.send("{}, {} : ERROR : UNKNOWN-ERROR".format(server_port, client_port).encode())
			raise

		# Send the ident from the file.
		connection.send("{}, {} : USERID : OTHER : {}".format(server_port, client_port, file_string).encode())
	elif args.random:
		# Use the first chunk of a random UUID.
		random_string = str(uuid.uuid4()).split("-")[0]

		# Send it to the client.
		connection.send("{}, {} : USERID : OTHER : {}".format(server_port, client_port, random_string).encode())
	elif args.static:
		# Send the static ident.
		connection.send("{}, {} : USERID : OTHER : {}".format(server_port, client_port, args.static).encode())
	elif args.error:
		# Respond with a HIDDEN-USER error.
		connection.send("{}, {} : ERROR : HIDDEN-USER".format(server_port, client_port).encode())
	else:
		# We don't have anything to send, error out.
		connection.send("{}, {} : ERROR : UNKNOWN-ERROR".format(server_port, client_port).encode())

	# Close the connection.
	connection.close()

# Main connection loop.
while True:
	# Wait for a connection.
	connection, address = server.accept()

	# Notice printing.
	print("NOTICE: Got a connection from {}.".format(address))

	# Pass it to our handler and move on.
	process = multiprocessing.Process(target = handle_connection, args = [connection, address])
	process.start()
