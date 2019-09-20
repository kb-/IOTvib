var colors = colormap({
    colormap: 'jet',
    nshades: 256,
    format: 'rgbaString',
    alpha: 1
});

window.colidx = [];
    
function drawSpectrogram(elt,x,y,z) {
  
  if(!document.getElementById("SpectrogramCanvas")){
    var container = document.createElement( 'div' );
    container.setAttribute("id", "SpectrogramCanvas");
    elt.appendChild( container );

    window.Spectrogramcanvas = container.appendChild(document.createElement('canvas'));
  }

  var ctx = Spectrogramcanvas.getContext('2d');
  
  var max = nj.max(z);
  var min = nj.min(z);
  
  var range = max-min;
  
  const col_range = colors.length;
  const width = x.length;
  const height = y.length;
  
  var imageData = ctx.getImageData(0, 0, width, height);
  var data = imageData.data;
  
  ctx.canvas.width  = width;
  ctx.canvas.height = height;  
  
  
  // let i;
  // let j;

  // for (i = 0; i < x.length; i++) {
    // for (j = 0; j < y.length; j++) {
      // let colorIdx = Math.floor(z[j][i]/range*col_range);
      // window.colidx.push(colorIdx);
      // ctx.fillStyle = colors[colorIdx];
      // ctx.fillRect(
        // i,
        // y.length - j,
        // 1,
        // 1
      // );
    // }
  // }
}

//drawSpectrogram($(placeholder2).get(0),spx,spy,spz)
//0: 0, max(z):255