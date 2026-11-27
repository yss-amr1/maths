import json,subprocess,os
os.chdir('/home/user/maths/video_edit')
L=lambda t,k='p':{'k':k,'t':t}
jobs=[]
def add(name,lines,pos='bottom:80px',fs=74): jobs.append({'W':1920,'H':1080,'fs':fs,'pos':pos,'lines':lines,'out':f'work/caps/main_{name}.png'})
add('st_olga',[L('OLGA')]);add('st_lee',[L('Lee Cooper')]);add('st_sf',[L('Smart Fit · Colin\'s')])
add('st_cin',[L('Cinerji سينما')]);add('st_cinw',[L('Cinerji سينما'),L('صورة: Le360','c')])
add('st_act',[L('Actionsport Outlet')]);add('st_may',[L('Maybelline')]);add('st_bf',[L('BLACK FRIDAY')]);add('st_food',[L('فضاء المطاعم')])
add('inaug',[L('افتتاح عين السبع مول'),L('صورة: Boursenews','c')])
json.dump(jobs,open('work/caps_main2.json','w'),ensure_ascii=False)
