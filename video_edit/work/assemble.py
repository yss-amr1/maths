import json,subprocess,sys,os
os.chdir('/home/user/maths/video_edit')
mode=sys.argv[1]            # preview|main
Y='{\\c&H4AD5FF&}'; Wc='{\\c&HFFFFFF&}'
import re
FS='{\\fs56}'
CAP={0:["جولة فـ مول","~عين السبع",FS+"BLACK FRIDAY"],1:["أجواء","~ما تتنساش"],2:["جولة بين","~المحلات"],
3:["عرض رقص","~خرافي"],4:["ماركات عالمية","~وديكور رائع"],6:["~تخفيضات",FS+"BLACK FRIDAY"],
7:["الطاقة","~والحماس"],8:["ديكور","~وأضواء روعة"],10:["الجمهور كله","~متفاعل"],11:["الجو كله","~حياة"],
13:["حركات","~ما تتفوتش"],14:["مول","~كبير وواسع"],16:["شكون","~كيبغي يعاود"],18:["عرض","~كيبقى فالبال"],
21:["~اشتركوا فالقناة",FS+"le monde de ines",FS+"عالم إيناس"]}
def conv(line):
    hi=line.startswith('~'); line=line.lstrip('~')
    pre=''
    m=re.match(r'(\{[^}]*\})(.*)',line)
    if m: pre,line=m.group(1),m.group(2)
    if re.search('[\u0600-\u06FF]',line): line=' '.join(reversed(line.split()))
    return (Y if hi else '')+pre+line+(Wc if hi else '')
T=json.load(open('work/timeline.json')); starts=[];t=0
for k,d in T: starts.append(t); t+=d
total=t
def ts(x): h=int(x//3600);m=int(x%3600//60);return f"{h}:{m:02d}:{x%60:05.2f}"
def ass(path,W,H,fs,mv,idx,tl):
    L=[f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\nWrapStyle: 2\n",
    f"[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding",
    f"Style: Default,DejaVu Sans,{fs},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,2,2,60,60,{mv},1",
    "\n[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text"]
    for new_i,i in enumerate(idx):
        if i in CAP:
            a=tl[new_i][0]+0.3; b=tl[new_i][0]+tl[new_i][1]-0.2
            txt="\\N".join(conv(x) for x in CAP[i]); 
            L.append(f"Dialogue: 0,{ts(a)},{ts(b)},Default,,0,0,0,,{{\\fad(200,150)\\t(0,250,\\fscx108\\fscy108)\\t(250,450,\\fscx100\\fscy100)}}{txt}")
    open(path,'w').write("\n".join(L)+"\n")
idx=list(range(len(T))); tl=[(starts[i],T[i][1]) for i in idx]
ass('work/main.ass',1920,1080,78,100,idx,tl)
# music gain automation: photo/B-roll/end high, under D lower
gains=[]
for i,(k,d) in enumerate(T):
    g=1.0 if k in('photo','end') else (0.62 if k=='D' else 0.9)
    gains.append(f"volume={g}:enable='between(t,{starts[i]:.2f},{starts[i]+d:.2f})'")
segs=[f'work/seg/{i:02d}.mp4' for i in idx]
inp=[];[inp.extend(['-i',s]) for s in segs]; inp+=['-i','work/music.wav']
n=len(segs)
fc="".join(f"[{i}:v][{i}:a]" for i in range(n))+f"concat=n={n}:v=1:a=1[v0][a0];"
fc+=f"[a0]volume=0.25[ev];[{n}:a]atrim=0:{total},{','.join(gains)}[m];"
fc+="[ev][m]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[aout];"
fc+="[v0]subtitles=work/main.ass[vout]"
out='out/preview_15s.mp4' if mode=='preview' else 'out/main_16x9.mp4'
cmd=['ffmpeg','-y','-v','error']+inp+['-filter_complex',fc,'-map','[vout]','-map','[aout]']
if mode=='preview': cmd+=['-t','15']
cmd+=['-r','30','-c:v','libx264','-crf','17','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',out]
r=subprocess.run(cmd,capture_output=True,text=True); print(r.stderr[-1500:] or 'ok',total)
