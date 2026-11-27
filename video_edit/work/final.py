import subprocess,os,json,sys
import numpy as np
os.chdir('/home/user/maths/video_edit'); sys.argv=['x','none']
src=open('work/assemble.py').read(); exec(src[:src.index("def conv")])
T=json.load(open('work/timeline.json'))
B=open('work/build.py').read(); ns={}; exec(B[B.index("T=["):B.index("def run")],ns); TT=ns['T']
def run(a):
    r=subprocess.run(['ffmpeg','-y','-v','error']+a,capture_output=True,text=True)
    if r.returncode: print(r.stderr[-1500:]); sys.exit(1)
def assemble(segfiles,tl,kinds,name,outp,cappre,W,H):
    N=len(segfiles); total=sum(d for _,d in tl)
    inp=[];[inp.extend(['-i',s]) for s in segfiles]; inp+=['-i','work/music.wav']
    gains=[f"volume={1.0 if k in('photo','end') else (0.62 if k=='D' else 0.9)}:enable='between(t,{s:.2f},{s+d:.2f})'" for (s,d),k in zip(tl,kinds)]
    fc="".join(f"[{i}:v][{i}:a]" for i in range(N))+f"concat=n={N}:v=1:a=1[v0][a0];[a0]volume=0.25[ev];[{N}:a]atrim=0:{total},{','.join(gains)}[m];"
    fc+="[ev][m]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[aout];"
    cur='v0'; k=N+1
    for n,i in enumerate(idx_list):
        f=f'work/caps/{cappre}_{i}.png'
        if not os.path.exists(f) or i not in CAP: continue
        a=tl[n][0]+0.3; b=tl[n][0]+tl[n][1]-0.2
        inp+=['-loop','1','-framerate','30','-t',f'{total:.2f}','-i',f]
        fc+=f"[{k}:v]format=rgba,fade=t=in:st={a:.2f}:d=0.2:alpha=1,fade=t=out:st={b-0.15:.2f}:d=0.15:alpha=1[c{k}];[{cur}][c{k}]overlay=enable='between(t,{a:.2f},{b:.2f})'[o{k}];"
        cur=f'o{k}'; k+=1
    fc=fc.rstrip(';').replace(f"[{cur}]",'[VOUT]',0)
    run(inp+['-filter_complex',fc,'-map',f'[{cur}]','-map','[aout]','-r','30','-c:v','libx264','-crf','23','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',outp])
# ---- main
if sys.argv and 'main' in os.environ.get('WHAT','main short'):
    starts=[];t=0
    for kk,d in T: starts.append(t); t+=d
    idx_list=list(range(len(T)))
    assemble([f'work/seg/{i:02d}.mp4' for i in idx_list],[(starts[i],T[i][1]) for i in idx_list],[k for k,_ in T],'main','out/main_16x9.mp4','main',1920,1080)
    print('main ok')
# ---- short
if 'short' in os.environ.get('WHAT','main short'):
    IDX=[1,3,5,7,9,10,12,13,15,16,21]; G=1/1.06; os.makedirs('work/sseg',exist_ok=True); tl=[];t=0
    for n,i in enumerate(IDX):
        k,s,ss,d,mv=TT[i]
        raw=subprocess.run(['ffmpeg','-v','error','-ss',str(ss),'-t',str(d),'-i','src/D.mov','-vf','fps=6,scale=106:60,format=gray','-f','rawvideo','-'],capture_output=True).stdout
        f=np.frombuffer(raw,np.uint8).reshape(-1,60,106).astype(np.float32)
        dif=np.abs(np.diff(f,axis=0)).sum(axis=(0,1)); dif=np.convolve(dif,np.ones(9)/9,'same')
        c=(dif*np.arange(106)).sum()/dif.sum()/106
        ww=720/848; x0=int(round(min(max(c-ww/2,0),1-ww)*848))//2*2
        grade=f"eq=contrast=1.07:saturation=1.18:gamma={G:.3f},colorbalance=rs=0.025:bs=-0.03"
        fgz="crop=720:480:%d:0,scale=1080:720:flags=lanczos,%s,unsharp=5:5:0.7:5:5:0"%(x0,grade)
        vf=("fps=30,split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=40,eq=brightness=-0.2:saturation=1.3[bg];"
            f"[b]{fgz}[fg];[bg][fg]overlay=0:600,format=yuv420p")
        af=f"highpass=f=70,afftdn=nr=10:nf=-45,lowpass=f=14000,afade=t=in:d=0.03,afade=t=out:st={d-0.03}:d=0.03"
        if mv=='end':
            vf+=f",eq=brightness=-0.22,fade=t=out:st={d-0.7}:d=0.7"; af=f"highpass=f=70,afftdn=nr=10:nf=-45,lowpass=f=14000,afade=t=out:st={d-1.2}:d=1.2"
        run(['-ss',str(ss),'-t',str(d),'-i','src/D.mov','-filter_complex',vf,'-af',af,'-ac','2','-ar','48000','-c:v','libx264','-crf','15','-preset','fast','-c:a','aac','-b:a','192k',f'work/sseg/{n:02d}.mp4'])
        tl.append((t,d)); t+=d
    idx_list=IDX
    assemble([f'work/sseg/{n:02d}.mp4' for n in range(len(IDX))],tl,[TT[i][0] for i in IDX],'short','out/short_9x16.mp4','short',1080,1920)
    print('short ok')
