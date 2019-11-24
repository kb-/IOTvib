importScripts('../js/cbuffer.js');

self.addEventListener('message', function(o) {
  var r = [];
  
  for(let i=0; i<o.data.cbufs.length; i++){//loop on tracks
    var spectrums = a2d_fill(o.data.cbufs[0].length,o.data.cbufs[0].data[0].length,0);//n spectrums x n lines
    for(let j=0; j<o.data.cbufs[i].length; j++){//loop on spectrums
      spectrums[j] = fft_int(o.data.cbufs[i].data[j], o.data.f, o.data.unit_conversion[i].int, o.data.unit_conversion[i].sc);
      if(spectrums[j][0]==Infinity)spectrums[j][0] = NaN;//flot addData can't handle Infinity
    }
    r.push(spectrums);
  }
 
  self.postMessage(r);
}, false);

//DO DO: when available in FF and Chrome, swicth to module
function fft_int(y,f,n,scale){
  return y.map(function(e,i,a){
    return e*scale/Math.pow(2*Math.PI*f[i],n);
  });
}

function a2d_fill(l,c,v){//line, column, value
  return Array.from(Array(l), _ => Array(c).fill(v));
}