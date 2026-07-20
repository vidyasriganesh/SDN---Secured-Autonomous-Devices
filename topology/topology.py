from mininet.topo import Topo


class IoTTopo(Topo):

    def build(self):

        # Switch
        s1 = self.addSwitch('s1')

        # IoT Device 1
        h1 = self.addHost(
            'h1',
            ip='10.0.0.1/24',
            mac='00:00:00:00:00:01'
        )

        # IoT Device 2
        h2 = self.addHost(
            'h2',
            ip='10.0.0.2/24',
            mac='00:00:00:00:00:02'
        )

        # IoT Device 3
        h3 = self.addHost(
            'h3',
            ip='10.0.0.3/24',
            mac='00:00:00:00:00:03'
        )

        # IoT Device 4
        h4 = self.addHost(
            'h4',
            ip='10.0.0.4/24',
            mac='00:00:00:00:00:04'
        )

        # IoT Device 5
        h5 = self.addHost(
            'h5',
            ip='10.0.0.5/24',
            mac='00:00:00:00:00:05'
        )

        # Links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s1)
        self.addLink(h5, s1)


topos = {
    'iottopo': (lambda: IoTTopo())
}
