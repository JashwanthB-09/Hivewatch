import socket, datetime, requests, threading, time

API_URL = "http://127.0.0.1:8000/api/log"
def severity(u, p, port):
    if (u or "").lower() in ["root", "admin"]: return "High"
    if port == 21 and p == "12345": return "High"
    if not u or not p: return "Low"
    return "Medium"

def send_log(data):
    def worker(d):
        for i in range(3):
            try: return requests.post(API_URL, json=d, timeout=3)
            except: time.sleep(1*(i+1))
    threading.Thread(target=worker, args=(data,), daemon=True).start()

def recv_line(c):
    try: return c.recv(1024).decode(errors="ignore").strip()
    except: return ""

def telnet(c,a):
    u=p=""
    try:
        c.send(b"Username: "); u=recv_line(c)
        c.send(b"Password: "); p=recv_line(c)
    finally: c.close()
    send_log({"timestamp":datetime.datetime.utcnow().isoformat(),
              "source_ip":a[0],"port_attacked":2323,"honeypot_type":"telnet",
              "payload":{"username":u,"password":p},"reported_severity":severity(u,p,2323)})

def ftp(c,a):
    u=p=""; c.send(b"220 FTP Honeypot Ready\r\n"); first=recv_line(c)
    if first.upper().startswith("USER"):
        u=first.split(maxsplit=1)[1] if len(first.split())>1 else ""
        c.send(b"331 Username ok\r\n"); second=recv_line(c)
        if second.upper().startswith("PASS"): p=second.split(maxsplit=1)[1] if len(second.split())>1 else ""
    elif ":" in first: u,p=first.split(":",1)
    else: u=first
    c.close()
    send_log({"timestamp":datetime.datetime.utcnow().isoformat(),
              "source_ip":a[0],"port_attacked":2121,"honeypot_type":"ftp",
              "payload":{"username":u,"password":p},"reported_severity":severity(u,p,2121)})

def listener(port,handler):
    s=socket.socket(); s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    s.bind(("0.0.0.0",port)); s.listen()
    while True:
        c,a=s.accept()
        threading.Thread(target=handler,args=(c,a),daemon=True).start()

if __name__=="main_":
    threading.Thread(target=listener,args=(23233,telnet),daemon=True).start()
    threading.Thread(target=listener,args=(21212,ftp),daemon=True).start()
    print("Honeypots running (telnet:2323, ftp:2121)")
    while True: time.sleep(1)
