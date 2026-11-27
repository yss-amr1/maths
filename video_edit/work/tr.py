import sys,json
from faster_whisper import WhisperModel
m=WhisperModel("small",device="cpu",compute_type="int8")
import numpy as np,wave
w=wave.open(sys.argv[1]);a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
segs,info=m.transcribe(a,language="ar",vad_filter=False,word_timestamps=False)
out=[{"s":round(s.start,2),"e":round(s.end,2),"t":s.text.strip()} for s in segs]
json.dump(out,open(sys.argv[2],"w"),ensure_ascii=False,indent=0)
for o in out: print(o["s"],o["e"],o["t"])
