#  PCAPX  
### Interactive Terminal-Based Packet Capture Tool for Linux

---

## Introduction

**PCAPX** is a lightweight, terminal-based packet capturing and analysis tool designed specifically for Linux users who prefer **speed, simplicity, and control** over heavy graphical interfaces.

It allows users to **capture packets live**, **analyze them interactively in the terminal**, and **automatically save them as `.pcap` files** — all while the capture is running.

PCAPX is built with a **learning-first and usability-first mindset**, making it ideal for:
- Cybersecurity students  
- Networking learners  
- Linux power users  
- Academic projects and demonstrations  

---

##  Why PCAPX?

While tools like Wireshark are extremely powerful, they also come with drawbacks:

- Heavy GUI dependency  
- High system resource usage  
- Complex interfaces for beginners  
- Not ideal for quick terminal-based analysis  

**PCAPX solves this by:**

✔ Working entirely in the terminal  
✔ Providing interactive controls during capture  
✔ Separating *capture* and *display* logic (like Wireshark)  
✔ Keeping the tool fast, simple, and transparent  

> **PCAPX = Wireshark-style control with terminal-level efficiency**

---

##  Features Breakdown

### 🔹 Live Packet Capture
- Real-time packet capturing using `tshark`
- Supports **multiple network interfaces simultaneously**
- Automatic `.pcap` file generation

---

### 🔹 Interactive Terminal Output
- Packets are displayed live as they are captured
- Minimal formatting for high performance
- Easy-to-read output

---

### 🔹 Color-Coded Protocols
| Protocol | Color |
|--------|------|
| TCP | Cyan |
| UDP | Green |
| ICMP | Yellow |
| Others | Magenta |

---

### 🔹 Pause / Resume Display
- Pause terminal output without stopping capture
- Resume anytime
- No packet loss
- Capture continues in background

---

### 🔹 Live Display Filters (Wireshark-Style)
Filters affect **only what you see**, not what is captured.

Examples:
- Protocol filter
- Port filter
- Host filter

The `.pcap` file always contains **all traffic**.

---

### 🔹 Packet Counters & PPS
- Total packet count
- Per-protocol counters
- Packets-per-second (PPS)
- Displayed **only when user issues a command** (no spam)

---

##  Installation Guide

Follow the steps below to install and set up **PCAPX** on a Linux system.

###  Clone the Repository
```bash
git clone https://github.com/Sec-x07/PCAPX.git
cd PCAPX
```
### Installation 
``` bash
chmod +x install.py
````
### Running the Tool 
``` bash
sudo python3 capture.py
```
##  Interactive Commands

You can type commands **while capture is running**:

### 🔸 Display Filters
```text
filter tcp
filter udp
filter icmp
filter port 80
filter host 8.8.8.8
filter clear
