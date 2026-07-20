class QuarantineManager:

    def __init__(self):

        self.blocked_devices = set()

    def quarantine(self, src_ip):

        self.blocked_devices.add(src_ip)

        print("=" * 50)
        print("DEVICE QUARANTINED")
        print("Blocked:", src_ip)
        print("=" * 50)

    def is_blocked(self, src_ip):

        return src_ip in self.blocked_devices
