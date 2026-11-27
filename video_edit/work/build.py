import subprocess,os,sys,json
W='/home/user/maths/video_edit/'; os.chdir(W)
SRC={'D':'src/D.mov','B1':'src/B1.mov','B2':'src/B2.mp4','B3':'src/B3.mp4','B4':'src/B4.mp4','B5':'src/B5.mp4'}
G={'D':1/1.06,'B1':1/1.19,'B2':1/0.97,'B3':1/0.8,'B4':1/1.18,'B5':1/1.07}
# (id, src, ss, dur, move)
T=[('photo',None,0,3.0,'ken'),('D','D',12,3.2,'punch'),('B1','B1',0,4.5,'push'),('D','D',22,4.5,'push'),
('B4','B4',1,5.0,'static'),('D','D',31,4.0,'punch'),('B3','B3',0.2,5.3,'push'),('D','D',40,5.0,'push'),
('B2','B2',0.5,5.5,'punch'),('D','D',49,4.0,'punch'),('D','D',55,4.5,'push'),('B5','B5',1,5.5,'push'),
('D','D',64,4.0,'punch'),('D','D',71,5.0,'push'),('B2','B2',6,4.5,'punch'),('D','D',80,4.0,'punch'),
('D','D',87,5.0,'push'),('B4','B4',8,5.0,'static'),('D','D',96,5.0,'push'),('B1','B1',5.5,4.5,'punch'),
('B5','B5',6,4.0,'push'),('end','D',101,3.5,'end')]
def run(a): 
    r=subprocess.run(['ffmpeg','-y','-v','error']+a,capture_output=True,text=True)
    if r.returncode: print(r.stderr[-1500:]); sys.exit(1)
os.makedirs('work/seg',exist_ok=True)
for i,(k,s,ss,d,mv) in enumerate(T):
    out=f'work/seg/{i:02d}.mp4'
    r=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',out],capture_output=True,text=True)
    try:
        if abs(float(r.stdout)-d)<0.2: print('skip',i,end=' ',flush=True); continue
    except: pass
    if k=='photo':
        vf=("crop=1280:720:0:130,scale=3840:2160:flags=lanczos,eq=contrast=1.05:saturation=1.15,"
            "zoompan=z='1.0+0.0016*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=90:s=1920x1080:fps=30,fade=t=in:d=0.35,format=yuv420p")
        run(['-i','src/photo.jpg','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-vf',vf,'-t',str(d),'-shortest',
             '-c:v','libx264','-crf','14','-preset','fast','-c:a','aac','-b:a','192k',out]); continue
    g=G[s]
    base=f"fps=30,scale=2880:1620:flags=lanczos,eq=contrast=1.07:saturation=1.18:gamma={g:.3f},colorbalance=rs=0.025:bs=-0.03"
    if mv=='push': z=f"zoompan=z='min(1+0.0010*on,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30"
    elif mv=='punch': z="crop=2592:1458,scale=1920:1080:flags=lanczos"
    elif mv=='end': z="scale=1920:1080:flags=lanczos,eq=brightness=-0.22,gblur=sigma=7"
    else: z="scale=1920:1080:flags=lanczos"
    vf=f"{base},{z},unsharp=5:5:0.5:5:5:0,format=yuv420p"
    if mv=='end': vf+=f",fade=t=out:st={d-0.7}:d=0.7"
    af=f"highpass=f=70,afftdn=nr=10:nf=-45,lowpass=f=14000,afade=t=in:d=0.03,afade=t=out:st={d-0.03}:d=0.03"
    if mv=='end': af=f"highpass=f=70,afftdn=nr=10:nf=-45,lowpass=f=14000,afade=t=out:st={d-1.2}:d=1.2"
    run(['-ss',str(ss),'-t',str(d),'-i',SRC[s],'-vf',vf,'-af',af,'-ac','2','-ar','48000','-c:v','libx264','-crf','15','-preset','fast','-c:a','aac','-b:a','192k',out])
    print('seg',i,end=' ',flush=True)
json.dump([(k,d) for k,s,ss,d,mv in T],open('work/timeline.json','w'))
print('done')
