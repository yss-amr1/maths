import numpy as np, wave
sr=48000; dur=108; bpm=104; beat=60/bpm
n=int(sr*dur); L=np.zeros(n); R=np.zeros(n)
def add(buf,t,x,g=1.0):
    i=int(t*sr); 
    if i>=n: return
    x=x[:n-i]; buf[i:i+len(x)]+=x*g
def env(l,a=0.005,d=8): 
    t=np.arange(l)/sr; return np.minimum(t/a,1)*np.exp(-d*t)
def midi(m): return 440*2**((m-69)/12)
def pluck(f,l=0.35):
    t=np.arange(int(sr*l))/sr
    return (np.sin(2*np.pi*f*t)+0.4*np.sin(4*np.pi*f*t)+0.2*np.sin(6*np.pi*f*t))*env(len(t),0.003,9)
def pad(f,l):
    t=np.arange(int(sr*l))/sr
    x=sum(np.sin(2*np.pi*f*(1+d)*t) for d in(-0.003,0,0.003))/3
    return x*np.minimum(t/0.4,1)*np.minimum((l-t)/0.4,1)
def kick(l=0.3):
    t=np.arange(int(sr*l))/sr; f=50+90*np.exp(-30*t)
    return np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-9*t)
rng=np.random.default_rng(1)
def hat(l=0.06): return rng.standard_normal(int(sr*l))*env(int(sr*l),0.001,60)
def clap(l=0.18): return rng.standard_normal(int(sr*l))*env(int(sr*l),0.002,22)
chords=[(57,60,64),(53,57,60),(48,52,55),(55,59,62)]  # Am F C G
bars=int(dur/(4*beat))
for b in range(bars):
    ch=chords[b%4]; t0=b*4*beat
    for m in ch: 
        p=pad(midi(m-12 if m>55 else m),4*beat); add(L,t0,p,0.10); add(R,t0,p,0.10)
    for k in range(8):                       # arpeggio 8ths
        m=ch[[0,1,2,1,0,1,2,1][k]]+12
        pl=pluck(midi(m)); tt=t0+k*beat/2
        add(L,tt,pl,0.16 if k%2==0 else 0.10); add(R,tt+0.012,pl,0.12)
    bass=pluck(midi(ch[0]-12),0.5)
    for q in (0,2): add(L,t0+q*beat,bass,0.28); add(R,t0+q*beat,bass,0.28)
    intro = b<2
    if not intro:
        for q in range(4):
            kk=kick(); add(L,t0+q*beat,kk,0.55); add(R,t0+q*beat,kk,0.55)
            h=hat(); add(L,t0+q*beat+beat/2,h,0.08); add(R,t0+q*beat+beat/2,h,0.08)
        for q in (1,3):
            c=clap(); add(L,t0+q*beat,c,0.14); add(R,t0+q*beat,c,0.14)
m=np.stack([L,R],1); m/=np.max(np.abs(m))*1.15
fade=int(sr*3); m[-fade:]*=np.linspace(1,0,fade)[:,None]
w=wave.open('work/music.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
w.writeframes((m*32767).astype(np.int16).tobytes()); w.close()
