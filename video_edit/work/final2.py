import subprocess,os,json,sys
os.chdir('/home/user/maths/video_edit')
def run(a):
    r=subprocess.run(['ffmpeg','-y','-v','error']+a,capture_output=True,text=True)
    if r.returncode: print(r.stderr[-1500:]); sys.exit(1)
T=json.load(open('work/timeline.json'))   # original 22 segs (kind,dur)
G={'B1':1/1.19,'B2':1/0.97,'B3':1/0.8,'B4':1/1.18,'B5':1/1.07,'W':1.0}
GS={'st_olga':'B1','st_lee':'B2','st_sf':'B2','st_cin':'B4','st_act':'B4','st_may':'B5','st_bf':'B5','st_food':'B3','st_cinw':'W','inaug':'W'}
# stills
def still(name,dur=2.4,zin=True):
    out=f'work/seg2/{name}.mp4'
    n=int(dur*30)+8; z="1+0.0012*on" if zin else "max(1.0,1.1-0.0012*on)"
    vf=(f"scale=2880:1620:flags=lanczos,eq=contrast=1.07:saturation=1.18:gamma={G[GS[name]]:.3f},colorbalance=rs=0.025:bs=-0.03,"
        f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s=1920x1080:fps=30,unsharp=5:5:0.5:5:5:0,format=yuv420p")
    run(['-i',f'work/stf/{name}.png','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-vf',vf,'-t',str(dur),'-shortest','-c:v','libx264','-crf','15','-preset','fast','-c:a','aac','-b:a','192k',out])
    return out
def build(segs,outp,W,H,music_gain,crf=23):
    # segs: dict(file,dur,kind,cap,tr)  tr=(transition,duration) into this seg
    N=len(segs); inp=[];[inp.extend(['-i',s['file']]) for s in segs]; inp+=['-i','work/music.wav']
    fc=''
    for i in range(N): fc+=f"[{i}:v]settb=AVTB,fps=30,format=yuv420p[v{i}];[{i}:a]aresample=48000,aformat=channel_layouts=stereo[a{i}];"
    cur='v0';ac='a0';Lm=segs[0]['dur'];starts=[0.0]
    for i in range(1,N):
        tn,td=segs[i]['tr']; off=Lm-td; starts.append(off)
        fc+=f"[{cur}][v{i}]xfade=transition={tn}:duration={td}:offset={off:.3f}[x{i}];[{ac}][a{i}]acrossfade=d={td}:c1=tri:c2=tri[ax{i}];"
        cur=f'x{i}';ac=f'ax{i}';Lm+=segs[i]['dur']-td
    total=Lm
    gains=','.join(f"volume={music_gain(s['kind'])}:enable='between(t,{st:.2f},{st+s['dur']:.2f})'" for s,st in zip(segs,starts))
    fc+=f"[{ac}]volume=0.25[ev];[{N}:a]atrim=0:{total:.2f},{gains}[m];[ev][m]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[aout];"
    k=N+1
    for s,st in zip(segs,starts):
        if not s.get('cap'): continue
        a=st+0.45; b=st+s['dur']-0.35
        inp+=['-loop','1','-framerate','30','-t',f'{total:.2f}','-i',s['cap']]
        fc+=f"[{k}:v]format=rgba,fade=t=in:st={a:.2f}:d=0.2:alpha=1,fade=t=out:st={b-0.15:.2f}:d=0.15:alpha=1[c{k}];[{cur}][c{k}]overlay=enable='between(t,{a:.2f},{b:.2f})'[o{k}];"
        cur=f'o{k}';k+=1
    run(inp+['-filter_complex',fc.rstrip(';'),'-map',f'[{cur}]','-map','[aout]','-r','30','-c:v','libx264','-crf',str(crf),'-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',outp])
    return total,starts
def cap(prefix,key): 
    f=f'work/caps/{prefix}_{key}.png'; return f if os.path.exists(f) else None
F='fade'
def mk(kind,file,dur,capf,tr): return dict(kind=kind,file=file,dur=dur,cap=capf,tr=tr)
if 'main' in os.environ.get('WHAT','main short'):
    S=[]
    def orig(i,tr=(F,0.3)):
        k,d=T[i]; S.append(mk(k,f'work/seg/{i:02d}.mp4',d,cap('main',i),tr))
    S.append(mk('photo','work/seg/00.mp4',T[0][1],cap('main',0),(F,0.3)))
    S.append(mk('still',still('inaug',2.8),2.8,cap('main','inaug'),(F,0.4)))
    for i in (1,2,3,4): orig(i)
    show=[('st_olga',True),('st_lee',False),('st_sf',True),('st_cin',False),('st_cinw',True),('st_act',False),('st_may',True),('st_bf',False),('st_food',True)]
    for n,(name,zi) in enumerate(show):
        S.append(mk('still',still(name,2.4,zi),2.4,cap('main',name),('fadewhite',0.45) if n==0 else ('smoothleft',0.35)))
    first=True
    for i in range(5,len(T)):
        if i==len(T)-1: orig(i,('fadeblack',0.7))
        else: orig(i,(F,0.45) if first else (F,0.3))
        first=False
    tot,st=build(S,'out/main_16x9.mp4',1920,1080,lambda k:1.0 if k in('photo','end','still') else (0.62 if k=='D' else 0.9))
    print('main ok',round(tot,1))
if 'short' in os.environ.get('WHAT','main short'):
    IDX=[1,3,5,7,9,10,12,13,15,16,21]
    sd=json.load(open('work/timeline.json'))
    S=[]
    for n,i in enumerate(IDX):
        k,d=T[i]; dd={1:3.2,3:4.5,5:4.0,7:5.0,9:4.0,10:4.5,12:4.0,13:5.0,15:4.0,16:5.0,21:3.5}[i]
        S.append(mk(k,f'work/sseg/{n:02d}.mp4',dd,cap('short',i),('fadeblack',0.5) if i==21 else (F,0.25)))
    tot,st=build(S,'out/short_9x16.mp4',1080,1920,lambda k:1.0 if k=='end' else 0.7)
    print('short ok',round(tot,1))
