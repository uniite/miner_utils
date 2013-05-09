import socket


class APIClient(object):
    def run_command(self, command):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("localhost", 4028))
        s.send(command)
        response = s.recv(8192)
        s.close()
        return response

    def parse_kv_pairs(self, data):
        pairs = data.split(",")
        name = pairs.pop(0)
        return name, dict([pair.split("=") for pair in pairs])

    def summary(self):
        data = self.run_command("summary").split("|")[1]
        return self.parse_kv_pairs(data)[1]

    def devs(self):
        data = self.run_command("devs").split("|")[1:-1]
        return dict([self.parse_kv_pairs(x) for x in data])


if __name__ == "__main__":
    api = APIClient()
    print api.summary()
    print api.devs()
