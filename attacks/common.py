from scapy.all import *
from models import Interface, Host
import ifaddr
import netifaces as ni

def find_display_name(id: str):
    """
    Find interface name that is human-readable.
    If nothing is found, the given id will be returned.
    """
    for adapter in ifaddr.get_adapters():
        name = adapter.name

        if type(name) is bytes:
            name = name.decode('utf-8')

        if name == id:
            return adapter.nice_name

    return id

def find_gateway(id: str):
    """
    Find gateway belonging to an interface.
    If no gateway is found, None is returned.
    """
    gateways = ni.gateways()

    for gateway, name, _ in gateways[ni.AF_INET]:
        if name == id:
            return gateway

    return None

def find_interfaces():
    """
    Find all network interfaces on the device and return
    an Interface object for each interface found.
    """
    interfaces = []

    for iface in ni.interfaces():
        try:
            info = ni.ifaddresses(iface)

            interfaces.append(Interface(
                find_display_name(iface),
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

def scan_hosts(interface: Interface):
    packets = Ether() / ARP()
    packets[Ether].dst = 'ff:ff:ff:ff:ff:ff'
    packets[ARP].pdst = interface.subnet

    responses, _ = srp(packets, iface=interface.name, timeout=2, verbose=0)

    hosts = [Host(response.psrc, response.hwsrc) for _, response in responses]

    ip_to_int = lambda ip: reduce(lambda r, e: r*2**8 + int(e), ip.split('.'), 0)

    hosts.sort(key=lambda h: ip_to_int(h.ip_addr))

    return hosts