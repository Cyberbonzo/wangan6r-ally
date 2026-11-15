"""Cliente CDP stdlib para a interface local do Steam (sem credenciais)."""
import base64,hashlib,json,os,socket,struct,urllib.request

class SteamCDP:
    def __init__(self):
        pages=json.load(urllib.request.urlopen('http://127.0.0.1:8080/json/list'))
        page=next(x for x in pages if x.get('title')=='SharedJSContext')
        from urllib.parse import urlparse
        u=urlparse(page['webSocketDebuggerUrl'])
        self.s=socket.create_connection((u.hostname,u.port or 8080),timeout=20)
        key=base64.b64encode(os.urandom(16)).decode()
        request=(f'GET {u.path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n').encode()
        self.s.sendall(request)
        header=b''
        while not header.endswith(b'\r\n\r\n'):header+=self.s.recv(1)
        assert b' 101 ' in header.split(b'\r\n')[0],header.split(b'\r\n')[0]
        accept=base64.b64encode(hashlib.sha1((key+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest())
        assert accept.lower() in header.lower()
        self.index=0
    def read(self,n):
        result=b''
        while len(result)<n:
            part=self.s.recv(n-len(result))
            if not part:raise EOFError('CDP desconectado')
            result+=part
        return result
    def send(self,payload,opcode=1):
        payload=payload.encode() if isinstance(payload,str) else payload
        n=len(payload);header=bytes([0x80|opcode])
        if n<126:header+=bytes([0x80|n])
        elif n<65536:header+=bytes([0x80|126])+struct.pack('!H',n)
        else:header+=bytes([0x80|127])+struct.pack('!Q',n)
        mask=os.urandom(4)
        self.s.sendall(header+mask+bytes(v^mask[i%4] for i,v in enumerate(payload)))
    def receive(self):
        combined=b''
        while True:
            a,b=self.read(2);op=a&15;n=b&127
            if n==126:n=struct.unpack('!H',self.read(2))[0]
            elif n==127:n=struct.unpack('!Q',self.read(8))[0]
            mask=self.read(4) if b&128 else None
            raw=self.read(n)
            if mask:raw=bytes(v^mask[i%4] for i,v in enumerate(raw))
            if op==9:self.send(raw,10);continue
            if op==8:raise EOFError('WebSocket fechado')
            combined+=raw
            if a&128:return json.loads(combined)
    def evaluate(self,expression):
        self.index+=1
        self.send(json.dumps({'id':self.index,'method':'Runtime.evaluate','params':{'expression':expression,'returnByValue':True,'awaitPromise':True}}))
        while True:
            result=self.receive()
            if result.get('id')!=self.index:continue
            if 'error' in result:raise RuntimeError(result['error'])
            result=result['result']
            if 'exceptionDetails' in result:raise RuntimeError(result['exceptionDetails'].get('text','JS exception'))
            return result['result'].get('value')

if __name__=='__main__':
    c=SteamCDP()
    print(json.dumps(c.evaluate("({shortcutMethods:Object.keys(SteamClient.Apps).filter(k=>/Shortcut|Overview|AppList/.test(k)),store:typeof appStore,remove:typeof SteamClient.Apps.RemoveShortcut})"),indent=2))
