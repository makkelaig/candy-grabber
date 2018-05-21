import sys
sys.path.insert(0, "..")
import time
from collections import OrderedDict

from opcua import ua, Server, instantiate
from opcua.common.xmlexporter import XmlExporter


if __name__ == "__main__":
    
    # setup our server
    server = Server()
    server.set_endpoint("opc.tcp://localhost:4840/freeopcua/server/")
    
    # setup our own namespace, not really necessary but should as spec
    uri = "http://examples.freeopcua.github.io"
    idx = server.register_namespace(uri)
    
    # get Objects node, this is where we should put our nodes
    objects = server.get_objects_node()
    
    # populating our address space
    candyGrabber = objects.add_object(idx, "CandyGrabber")
    candyGrabber.add_property(0, "State", "Stopped")
    candyGrabber.add_property(0, "Mode", "None")
    start = candyGrabber.add_variable(idx,"Start", False)
    start.set_writable()        # Set MyVariable to be writable by clients
    stop = candyGrabber.add_variable(idx,"Stop", False)
    stop.set_writable()
    direction = candyGrabber.add_variable(idx, "Direction", "none")
    direction.set_writable()
    #move = candyGrabber.add_method(idx, "move", move_claw , [ua.VariantType.String])
    
    
    mydevice = instantiate(server.nodes.objects, dev, bname="2:Device0001")
    
    node_list = [candyGrabber, start, stop, direction]
    
    # starting!
    server.start()
    
    exporter = XmlExporter(server)
    exporter.build_etree(node_list, ['http://myua.org/test/'])
    exporter.write_xml('ua-export.xml')
    
    server.stop()