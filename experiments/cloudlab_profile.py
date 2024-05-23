"""An example of constructing a multisite lan.

Instructions:
Wait for the profile instance to start, and then log in to the nodes.
"""

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg

BANDWIDTH_WAN = 10000
LATENCY_WAN = 15

BANDWIDTH_LOCAL = 10000
LATENCY_LOCAL = 1

# Create a portal context.
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

# Create three raw "PC" nodes, one at each site
servers = []
for i in ["1", "2", "3"]:
  node = request.RawPC("node" + i)
  ifaces = []
  for j in ["1", "2", "3"]:
    iface = node.addInterface()
    ifaces.append(iface)
  servers.append(ifaces)

clients = []
for i in ["4", "5", "6"]:
  node = request.RawPC("node" + i)
  iface = node.addInterface()
  clients.append(iface)

for i in ["0", "1", "2"]:
  link = request.Link("link" + i)
  link.bandwidth = BANDWIDTH_WAN
  link.latency = LATENCY_WAN
  if i == "0":
    link.addInterface(servers[0][0])
    link.addInterface(servers[1][0])
  if i == "1":
    link.addInterface(servers[0][1])
    link.addInterface(servers[2][0])
  if i == "2":
    link.addInterface(servers[1][1])
    link.addInterface(servers[2][1])

for i in ["4", "5", "6"]:
  link = request.Link("link" + i)
  link.bandwidth = BANDWIDTH_LOCAL
  link.latency = LATENCY_LOCAL
  if i == "4":
    link.addInterface(clients[0])
    link.addInterface(servers[0][2])
  if i == "5":
    link.addInterface(clients[1])
    link.addInterface(servers[1][2])
  if i == "6":
    link.addInterface(clients[2])
    link.addInterface(servers[2][2])

pc.printRequestRSpec(request)