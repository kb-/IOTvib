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
  const height = y[y.length-1];//y.length;
  
  var imageData = ctx.getImageData(0, 0, width, height);
  var data = imageData.data;
  
  ctx.canvas.width  = width;
  ctx.canvas.height = height;  

  
  
  // let i;
  // let j;
  
  
}

//drawSpectrogram($(placeholder2).get(0),spx,spy,spz)
//0: 0, max(z):255