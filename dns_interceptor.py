import os
import signal
import sys
from dnslib import DNSRecord, RR, A, QTYPE
from socketserver import UDPServer, BaseRequestHandler

CONFIG_PATH = "/etc/NetworkManager/NetworkManager.conf"
ORIGINAL_CONFIG = """
[main]
plugins=ifupdown,keyfile
[ifupdown]
managed=false
"""

MODIFIED_CONFIG = """
[main]
plugins=ifupdown,keyfile
dns=none
[ifupdown]
managed=false
"""

def write_config(data):
    with open(CONFIG_PATH, "w") as f:
        f.write(data)

def restart_network_manager():
    os.system("systemctl restart NetworkManager")

def restore_config_and_exit(*args):
    print("\n[*] Restoring original NetworkManager config...")
    write_config(ORIGINAL_CONFIG)
    restart_network_manager()
    print("[+] DNS restored. Exiting.")
    sys.exit(0)

class DNSHandler(BaseRequestHandler):
    def handle(self):
        data = self.request[0]
        dns_req = DNSRecord.parse(data)
        qname = dns_req.q.qname
        reply = dns_req.reply()
        reply.add_answer(RR(qname, QTYPE.A, rdata=A("192.168.63.3"), ttl=60))
        self.request[1].sendto(reply.pack(), self.client_address)

def main():
    print("[1] Start fake DNS server")
    print("[2] Restore DNS and exit")
    choice = input("> ").strip()

    if choice == "2":
        restore_config_and_exit()

    print("[*] Updating NetworkManager config...")
    write_config(MODIFIED_CONFIG)
    restart_network_manager()
    print("[+] Config updated. Fake DNS starting on port 53...")

    signal.signal(signal.SIGINT, restore_config_and_exit)
    UDPServer(("0.0.0.0", 53), DNSHandler).serve_forever()

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("This script must be run as root.")
        sys.exit(1)
    main()
