"""ROG Ally controller bridge for the documented WIO1 input protocol."""
import ctypes as C
import os,signal,struct,time,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BLOCK=ROOT/'userdata/runtimes/mt6r/input.block'
TEST=ROOT/'logs/test-input.json'
os.environ['SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS']='1'
os.environ['SDL_GAMECONTROLLER_ALLOW_STEAM_VIRTUAL_GAMEPAD']='0'
os.environ.pop('SDL_GAMECONTROLLER_IGNORE_DEVICES',None)
for key in ('SteamAppId','SteamGameId','SteamVirtualGamepadInfo','SteamOverlayGameId'):
    os.environ.pop(key,None)
os.environ['SDL_JOYSTICK_HIDAPI']='0'
s=C.CDLL('libSDL2-2.0.so.0')
def bind(lib,n,r,a):
    f=getattr(lib,n);f.restype=r;f.argtypes=a;return f
bind(s,'SDL_Init',C.c_int,[C.c_uint32])(0x2200)
op=bind(s,'SDL_GameControllerOpen',C.c_void_p,[C.c_int])
axis=bind(s,'SDL_GameControllerGetAxis',C.c_int16,[C.c_void_p,C.c_int])
button=bind(s,'SDL_GameControllerGetButton',C.c_uint8,[C.c_void_p,C.c_int])
attached=bind(s,'SDL_GameControllerGetAttached',C.c_int,[C.c_void_p])
close=bind(s,'SDL_GameControllerClose',None,[C.c_void_p])
name=bind(s,'SDL_GameControllerName',C.c_char_p,[C.c_void_p])
running=True
def stop(*_):
    global running
    running=False
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
def game_pids():
    found=[]
    for p in Path('/proc').glob('[0-9]*'):
        try:
            command=(p/'cmdline').read_bytes().decode(errors='replace').replace('\\','/')
            if (p/'comm').read_text().strip()=='wmn6r.exe' and '/'+ROOT.name+'/userdata/runtimes/mt6r/' in command:
                found.append(int(p.name))
        except (OSError,ValueError):pass
    return found
def set_pause(value):
    for pid in game_pids():
        try:os.kill(pid,signal.SIGSTOP if value else signal.SIGCONT)
        except ProcessLookupError:pass
pad=None;fd=None;seq=0;gear=1;coins=0;old=set();paused=False;last_status=0
try:
    while running:
        now=time.monotonic()
        s.SDL_PumpEvents();s.SDL_GameControllerUpdate()
        if pad and not attached(pad):close(pad);pad=None
        if not pad:
            for i in range(s.SDL_NumJoysticks()):
                if s.SDL_IsGameController(i):
                    pad=op(i)
                    if pad:print('Controller:',name(pad).decode(),flush=True);break
        pressed={i for i in range(15) if pad and button(pad,i)}
        wheel=axis(pad,0)/32767 if pad else 0
        wheel=0 if abs(wheel)<.12 else (abs(wheel)-.12)/.88*(1 if wheel>0 else -1)
        gas=max(0,axis(pad,5)/32767) if pad else 0
        brake=max(0,axis(pad,4)/32767) if pad else 0
        if 13 in pressed:wheel=-1
        if 14 in pressed:wheel=1
        if 0 in pressed:gas=1
        if 1 in pressed:brake=1
        if TEST.exists():
            try:
                t=json.loads(TEST.read_text())
                if time.time()-TEST.stat().st_mtime<10:
                    pressed=set(t.get('buttons',[]));wheel=t.get('wheel',0);gas=t.get('gas',0);brake=t.get('brake',0)
            except (OSError,ValueError):pass
        edge=pressed-old
        if fd is not None and (not BLOCK.exists() or os.fstat(fd).st_ino!=BLOCK.stat().st_ino):
            os.close(fd);fd=None
        if fd is None and BLOCK.exists():fd=os.open(BLOCK,os.O_RDWR)
        if fd is not None:
            if 6 in edge or (paused and 0 in edge):
                paused=not paused;set_pause(paused);print('Pause:',paused,flush=True)
            if 10 in edge:gear=min(6,gear+1)
            if 9 in edge:gear=max(0,gear-1)
            b=bytearray(57);b[:4]=b'WIO1';seq=(seq+1)&0xffffffff
            struct.pack_into('<I',b,4,seq)
            # Buttons are JVS cabinet switch bits; analogs occupy high bytes.
            b[9]=(0x20 if 11 in pressed else 0)|(0x10 if 12 in pressed else 0)
            b[10]=(0,0xa0,0x60,0x80,0x40,0x90,0x50)[gear]|(2 if 3 in pressed else 0)|(1 if 2 in pressed else 0)
            b[11]=4 if 4 in pressed else 0
            if paused:wheel=gas=brake=0;b[9:13]=bytes(4)
            b[25]=min(236,20+round((max(-1,min(1,wheel))+1)*32767.5)//303)
            b[27]=round(max(0,min(1,gas))*255);b[29]=round(max(0,min(1,brake))*255)
            os.pwrite(fd,b,0)
        if now-last_status>1:
            last_status=now
            (ROOT/'logs/controls-status.json').write_text(json.dumps({'controller':name(pad).decode() if pad else None,'paused':paused,'sequence':seq,'gear':gear,'wheel':wheel,'gas':gas,'brake':brake}))
        old=pressed;time.sleep(.008)
finally:
    if paused:set_pause(False)
    if fd is not None:
        b=bytearray(57);b[:4]=b'WIO1';b[25]=128;os.pwrite(fd,b,0);os.close(fd)
    if pad:close(pad)
    s.SDL_Quit()
