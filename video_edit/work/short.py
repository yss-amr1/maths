import subprocess,os,json,sys
sys.argv=['x','none']
import numpy as np
os.chdir('/home/user/maths/video_edit')
src=open('work/assemble.py').read(); exec(src[:src.index("idx=list(range(len(T)))")])
exec(open('work/build.py').read().split("def run")[0].split("W='/home")[0])  # imports only
B=open('work/build.py').read(); ns={}
exec(B[B.index("T=["):B.index("def run")],ns); TT=ns['T']
G=1/1.06
IDX=[1,3,5,7,9,10,12,13,15,16,21]
def run(a):
    r=subprocess.run(['ffmpeg','-y','-v','error']+a,capture_output=True,text=True)
    if r.returncode: print(r.stderr[-1200:]); sys.exit(1)
os.makedirs('work/sseg',exist_ok=True); tl=[];t=0;info=[]
for n,i in enumerate(IDX):
    k,s,ss,d,mv=TT[i]
    raw=subprocess.run(['ffmpeg','-v','error','-ss',str(ss),'-t',str(d),'-i','src/D.mov','-vf','fps=6,scale=106:60,format=gray','-f','rawvideo','-'],capture_output=True).stdout
    f=np.frombuffer(raw,np.uint8).reshape(-1,60,106).astype(np.float32)
    dif=np.abs(np.diff(f,axis=0)).sum(axis=(0,1)); dif=np.convolve(dif,np.ones(9)/9,'same')
    c=(dif*np.arange(106)).sum()/dif.sum()/106 if dif.sum()>0 else 0.5
    ww=270/848; x0=int(round(min(max(c-ww/2,0),1-ww)*848)); info.append(round(c,2))
    vf=f"fps=30,crop=270:480:{x0}:0,scale=1080:1920:flags=lanczos,eq=contrast=1.07:saturation=1.18:gamma={G:.3f},colorbalance=rs=0.025:bs=-0.03,unsharp=5:5:0.5:5:5:0,format=yuv420p"
    af=f"highpass=f=70,afftdn=nr=10:nf=-45,lowpass=f=14000,afade=t=in:d=0.03,afade=t=out:st={d-0.03}:d=0.03"
    if mv=='end':
        vf=vf.replace("unsharp","eq=brightness=-0.22,gblur=sigma=7,unsharp")+f",fade=t=out:st={d-0.7}:d=0.7"
        af=f"highpass=f=70,afftdn=nr=10:nf=-45,lowpass=f=14000,afade=t=out:st={d-1.2}:d=1.2"
    run(['-ss',str(ss),'-t',str(d),'-i','src/D.mov','-vf',vf,'-af',af,'-ac','2','-ar','48000','-c:v','libx264','-crf','15','-preset','fast','-c:a','aac','-b:a','192k',f'work/sseg/{n:02d}.mp4'])
    tl.append((t,d)); t+=d
total=t; print('centroids',info,'total',total)
ass('work/short.ass',1080,1920,84,430,IDX,tl)
inp=[];[inp.extend(['-i',f'work/sseg/{n:02d}.mp4']) for n in range(len(IDX))]; inp+=['-i','work/music.wav']
N=len(IDX)
gains=[f"volume={1.0 if TT[i][0]=='end' else 0.7}:enable='between(t,{tl[n][0]:.2f},{tl[n][0]+tl[n][1]:.2f})'" for n,i in enumerate(IDX)]
fc="".join(f"[{i}:v][{i}:a]" for i in range(N))+f"concat=n={N}:v=1:a=1[v0][a0];[a0]volume=0.25[ev];[{N}:a]atrim=0:{total},{','.join(gains)}[m];"
fc+="[ev][m]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[aout];[v0]subtitles=work/short.ass[vout]"
run(inp+['-filter_complex',fc,'-map','[vout]','-map','[aout]','-r','30','-c:v','libx264','-crf','17','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart','out/short_9x16.mp4'])
print('ok')
