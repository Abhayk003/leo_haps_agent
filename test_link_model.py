from link_model import leo_link

def show(label, result):
    print(f"{label:22s} SNR {result['snr_db']:6.1f} dB   "
          f"capacity {result['capacity_mbps']:6.0f} Mbps   "
          f"delay {result['delay_ms']:5.2f} ms")

show("10 deg, clear", leo_link(10.0, 1649.0, raining=False))
show("10 deg, heavy rain", leo_link(10.0, 1649.0, raining=True))
show("72.3 deg, clear", leo_link(72.3, 503.6, raining=False))
show("72.3 deg, heavy rain", leo_link(72.3, 503.6, raining=True))