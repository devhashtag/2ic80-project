import netifaces as ni
from util import Interface

def find_gateway(id: str):
    gateways = ni.gateways()

    for gateway, name, _ in gateways[ni.AF_INET]:
        if name == id:
            return gateway

    return None

def find_interfaces():
    interfaces = []

    for iface in ni.interfaces():
        try:
            info = ni.ifaddresses(iface)

            interfaces.append(Interface(
                iface,
                info[ni.AF_INET][0]['addr'],
                info[ni.AF_LINK][0]['addr'],
                info[ni.AF_INET][0]['netmask'],
                find_gateway(iface)))
        except:
            """
            If we for some reason cannot find information
            on a certain interface, we skip the interface
            since we need all information to implement the
            attacks.
            """
            pass

    return interfaces