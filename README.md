# ARP-Spoofer
Assessment Task for CSCI369 Ethical Hacking - Q1 Develop an ARP spoofer using Scapy


This ARP spoofing tool poisons the ARP cache of both the victim machine and the router. This forces all traffic between them to pass through the attacker's machine.

Required to run:
- Kali Linux machine (attacker)
- Metasploitable (victim)
- Both machines must be on the same network (NAT)
- Python 3
- Scapy library

Network:
Ensure both machines are on NAT networking

Software Installs:
- Update package list 
    sudo apt update

- Install Python3 if not already installed
    sudo apt install python3

- Install pip if not already installed
    sudo apt install python3-pip

- Install Scapy
    sudo pip3 install scapy

IP forwarding:
- This will automatically be set up in the python code but you can do it manually prior to running the code with the following command
    sudo sysctl -w net.ipv4.ip_forward=1

IP Adresses:
    On Kali:
    
    - Get your interface name and IP
        ip a

    - Get your default gateway (router) IP
        ip route | grep default
    
    On Metasploitable
    - Get your victim machine IP
        ifconfig

Run Program:

    sudo python3 arpspoof.py <Victim_IP> <Router_IP>

Check if the spoof worked:
- You can use wireshark or 'sudo tcpdump -i eth0 arp' to see the ARP replies.
- You can use the command 'arp -a' on metasploitable to check the ARP tables showing the MAC address of the router is now the MAC address of the attacker

Example of a successful tcpdump:
- If you ran the code with this command 'sudo python3 arpspoof.py 10.0.2.7 10.0.2.1' (victim: 10.0.2.7, router: 10.0.2.1)
- A successful spoof tcpdump output would look like this:
    10:46:23.358496 eth0  Out ARP, Reply 10.0.2.7 is-at 08:00:27:e9:85:b5
    10:46:24.608804 eth0  Out ARP, Reply 10.0.2.1 is-at 08:00:27:e9:85:b5
Both the Router and Victim have the same MAC address

