const {chromium}=require('playwright');const fs=require('fs');
(async()=>{
 const jobs=JSON.parse(fs.readFileSync(process.argv[2]));
 const b=await chromium.launch();
 for(const j of jobs){
  const p=await b.newPage({viewport:{width:j.W,height:j.H}});
  const lines=j.lines.map(l=>{
    const cls=l.k; return `<div class="${cls}">${l.t}</div>`}).join('');
  await p.setContent(`<html><body style="margin:0;background:transparent;width:${j.W}px;height:${j.H}px;position:relative">
  <style>div.box{position:absolute;left:0;right:0;${j.pos};text-align:center;direction:rtl;font-family:'DejaVu Sans';font-weight:700;color:#fff;line-height:1.18}
  .box div{font-size:${j.fs}px;-webkit-text-stroke:${j.fs*0.14}px #000;paint-order:stroke fill;text-shadow:0 4px 10px rgba(0,0,0,.6)}
  .box div.p{display:inline-block;background:rgba(0,0,0,.58);padding:8px 38px 12px;border-radius:44px;-webkit-text-stroke:0;text-shadow:none;unicode-bidi:plaintext;font-size:${j.fs*0.86}px}.box div.c{font-size:${j.fs*0.42}px;-webkit-text-stroke:0;opacity:.85;margin-top:10px;unicode-bidi:plaintext}.box div.y{color:#FFD54A}.box div.l{font-size:${j.fs*0.72}px;direction:ltr}
  </style><div class="box">${lines}</div></body></html>`);
  await p.screenshot({path:j.out,omitBackground:true});
  await p.close();
 }
 await b.close();
})();
