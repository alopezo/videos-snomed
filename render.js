// Render a video folder's index.html to MP4 (or to single PNG frames).
// Usage: node render.js videos/<name> <out.mp4>         full silent video
//        node render.js videos/<name> x 3,20,42        frames → videos/<name>/build/shot_N.png
const {chromium}=require('playwright');const {spawn}=require('child_process');const path=require('path');const fs=require('fs');
(async()=>{
 const fps=30,dir=path.resolve(process.argv[2]),out=process.argv[3],only=process.argv[4];
 fs.mkdirSync(`${dir}/build`,{recursive:true});
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:540,height:960},deviceScaleFactor:2});
 await p.goto('file://'+dir+'/index.html');await p.waitForLoadState('networkidle');await p.evaluate(()=>document.fonts.ready);
 if(only){for(const t of only.split(',')){await p.evaluate(t=>render(t),+t);await p.screenshot({path:`${dir}/build/shot_${t}.png`})}await b.close();return}
 const total=await p.evaluate(()=>TOTAL);
 const ff=spawn('ffmpeg',['-y','-f','image2pipe','-framerate',''+fps,'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-preset','medium','-movflags','+faststart',path.resolve(out)],{stdio:['pipe','ignore','inherit']});
 for(let i=0;i<total*fps;i++){await p.evaluate(t=>render(t),i/fps);const buf=await p.screenshot({type:'jpeg',quality:92});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));}
 ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();
})();
