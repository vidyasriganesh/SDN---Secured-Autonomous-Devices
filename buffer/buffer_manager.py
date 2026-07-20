import json
import os
from datetime import datetime


class BufferManager:

    def __init__(self):

        self.buffer_folder = "./"

    def save(self, packet):

        filename = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        path = os.path.join(
            self.buffer_folder,
            filename + ".json"
        )

        with open(path, "w") as file:

            json.dump(packet, file, indent=4)

        return path
