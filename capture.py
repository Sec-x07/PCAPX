import subprocess
import signal
import time
import os
import threading
from datetime import datetime

# --------COLORS--------
RESET = "\033[0m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
BOLD = "\033[1m"

# -------- CONFIG --------
CAPTURE_DIR = "captures"
os.makedirs(CAPTURE_DIR, exist_ok=True)
# -----------------------

# -------- LIST INTERFACES --------
print(f"\n{BOLD}Available Interfaces{RESET}")
iface_out = subprocess.run(
    ["tshark", "-D"],
    capture_output=True,
    text=True
).stdout.splitlines()

for line in iface_out:
    print(line)

print(
    f"\n{YELLOW}Enter interface numbers (comma separated){RESET}\n"
    f"(example: 1,2 | leave empty for ALL)"
)

iface_input = input("Interfaces > ").strip()

interfaces = []
if iface_input:
    for part in iface_input.split(","):
        part = part.strip()
        if part.isdigit():
            interfaces.append(part)

if not interfaces:
    interfaces = ["any"]

# -------- FILE SETUP --------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
pcap_file = os.path.join(CAPTURE_DIR, f"capture_{timestamp}.pcap")

print(f"\n{GREEN}Saving capture to:{RESET} {pcap_file}")
print(
    f"{GREEN}Commands:{RESET}\n"
    f"  filter tcp | udp | icmp | port 80 | host 8.8.8.8\n"
    f"  filter clear\n"
    f"  pause | resume\n"
    f"  stop\n"
)

# -------- BUILD TSHARK CMD --------
cmd = ["tshark", "-l", "-w", pcap_file]

for iface in interfaces:
    cmd += ["-i", iface]

cmd += [
    "-T", "fields",
    "-e", "ip.src",
    "-e", "ip.dst",
    "-e", "tcp.srcport",
    "-e", "tcp.dstport",
    "-e", "udp.srcport",
    "-e", "udp.dstport",
    "-e", "frame.protocols",
    "-E", "separator=|"
]

proc = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True,
    bufsize=1
)

# -------- SHARED STATE --------
running = True
paused = False
display_filter = "ALL"

total = tcp_count = udp_count = icmp_count = 0
last_total = 0
last_time = time.time()
pps = 0

lock = threading.Lock()


# -------- STATUS PRINTER --------
def print_status():
    state = "PAUSED" if paused else "RUNNING"
    print(
        f"{BOLD}TOTAL:{RESET} {total} | "
        f"{CYAN}TCP:{RESET} {tcp_count} | "
        f"{GREEN}UDP:{RESET} {udp_count} | "
        f"{YELLOW}ICMP:{RESET} {icmp_count} | "
        f"{MAGENTA}PPS:{RESET} {pps} | "
        f"FILTER: {display_filter} | "
        f"STATE: {state}"
    )


# -------- FILTER LOGIC --------
def packet_matches_filter(src, dst, proto, ports):
    if display_filter == "ALL":
        return True

    f = display_filter.lower()

    if f in ("tcp", "udp", "icmp"):
        return f in proto

    if f.startswith("port "):
        port = f.split()[1]
        return port in ports

    if f.startswith("host "):
        host = f.split()[1]
        return src == host or dst == host

    return True


# -------- PACKET READER --------
def packet_reader():
    global total, tcp_count, udp_count, icmp_count, pps, last_total, last_time

    while running:
        line = proc.stdout.readline()
        if not line:
            break

        parts = line.strip().split("|")
        if len(parts) < 7:
            continue

        src, dst, tcp_sp, tcp_dp, udp_sp, udp_dp, proto = parts
        proto_l = proto.lower()
        ports = [tcp_sp, tcp_dp, udp_sp, udp_dp]

        with lock:
            total += 1
            if "tcp" in proto_l:
                tcp_count += 1
            elif "udp" in proto_l:
                udp_count += 1
            elif "icmp" in proto_l:
                icmp_count += 1

            now = time.time()
            if now - last_time >= 1:
                pps = total - last_total
                last_total = total
                last_time = now

        if paused:
            continue

        if not packet_matches_filter(src, dst, proto_l, ports):
            continue

        if "tcp" in proto_l:
            color = CYAN
            proto_name = "TCP"
        elif "udp" in proto_l:
            color = GREEN
            proto_name = "UDP"
        elif "icmp" in proto_l:
            color = YELLOW
            proto_name = "ICMP"
        else:
            color = MAGENTA
            proto_name = proto_l.upper()

        print(
            f"{color}{src:>15} -> {dst:<15}  {proto_name}{RESET}"
        )


# -------- INPUT LISTENER --------
def input_listener():
    global running, paused, display_filter

    while running:
        cmd = input().strip().lower()

        if cmd == "stop":
            print_status()
            running = False
            break

        if cmd == "pause":
            paused = True
            print_status()
            continue

        if cmd == "resume":
            paused = False
            print_status()
            continue

        if cmd.startswith("filter "):
            value = cmd.replace("filter ", "", 1)
            if value == "clear":
                display_filter = "ALL"
            else:
                display_filter = value.upper()
            print_status()


# -------- START THREADS --------
threading.Thread(target=packet_reader, daemon=True).start()
threading.Thread(target=input_listener, daemon=True).start()

# -------- WAIT LOOP --------
try:
    while running:
        time.sleep(0.2)
except KeyboardInterrupt:
    running = False

# -------- STOP & SAVE --------
print(f"\n{YELLOW}Stopping capture...{RESET}")
proc.send_signal(signal.SIGINT)
proc.wait()
time.sleep(1)

if os.path.exists(pcap_file) and os.path.getsize(pcap_file) > 0:
    print(f"{GREEN}✓ Capture saved:{RESET} {pcap_file}")
else:
    print(f"{MAGENTA}✗ Capture failed or empty file{RESET}")
