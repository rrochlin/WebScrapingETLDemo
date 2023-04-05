import threading
import queue
import requests
import pandas as pd
import pickle

q = queue.Queue()
valid_proxies = []

proxies = pd.read_excel("proxies.xlsx")
US_proxy_ips = proxies[proxies.Country == "United States"]["IP Address"].values
US_proxy_ports = proxies[proxies.Country == "United States"]["Port"].values

for ip, port in zip(US_proxy_ips, US_proxy_ports):
    q.put(ip + ":" + str(port))


def check_proxies():
    global q
    while not q.empty():
        proxy = q.get()
        try:
            res = requests.get("http://ipinfo.io/json",
                               proxies={"http": proxy, "https:": proxy})
        except Exception:
            continue
        if res.status_code == 200:
            valid_proxies.append(proxy)
            print(proxy)


for _ in range(10):
    threading.Thread(target=check_proxies).start()

with open("valid_proxies.pkl", "wb") as file:
    pickle.dump(valid_proxies, file)
