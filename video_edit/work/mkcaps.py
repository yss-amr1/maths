import json,sys,os,re
os.chdir('/home/user/maths/video_edit'); sys.argv=['x','none']
src=open('work/assemble.py').read(); exec(src[:src.index("def conv")])
def lines(c):
    out=[]
    for l in c:
        l=l.replace(FS,'')
        if l.startswith('~'): out.append({'k':'y','t':l[1:]})
        elif re.search('[؀-ۿ]',l): out.append({'k':'w','t':l})
        else: out.append({'k':'l','t':l})
    return out
for name,W,H,fs,pos in [('main',1920,1080,78,'bottom:70px'),('short',1080,1920,84,'top:1390px')]:
    jobs=[{'W':W,'H':H,'fs':fs,'pos':pos,'lines':lines(c),'out':f'work/caps/{name}_{i}.png'} for i,c in CAP.items()]
    json.dump(jobs,open(f'work/caps_{name}.json','w'),ensure_ascii=False)
