//https://plot.ly/javascript/reference/#surface-hoverinfo//
//or
//https://plot.ly/javascript/reference/#surface-hovertemplate
//https://plot.ly/javascript/reference/#surface-colorbar-tickfont
//https://plot.ly/javascript/reference/#surface-colorbar-tickfont-size
//https://plot.ly/javascript/reference/#surface-colorscale
//https://plot.ly/javascript/reference/#surface-hoverlabel
//ok https://plot.ly/javascript/reference/#layout-scene-camera-projection
//ok https://plot.ly/javascript/reference/#layout-scene-aspectratio
//https://plot.ly/javascript/reference/#layout-scene-xaxis-title-text
//https://plot.ly/javascript/reference/#layout-scene-xaxis-type linear/log
//https://plot.ly/javascript/reference/#layout-scene-annotations-items-annotation-captureevents
//
//update
//https://plot.ly/javascript/plotlyjs-function-reference/#plotlynewplot

// import
//<script type="text/javascript" src="./plotly-latest.min.js" charset="utf-8"></script>
var jet = colormap({nshades:6,colormap:"jet",format:"rgb"});
var idx = arraytools.linspace(5,0,6).map(e=>1/Math.pow(10,e));
idx[0] = 0;
var jetlog = jet.map((e,i)=>({index:idx[i], rgb:e.slice(0,3)}));

export function surf(divId,x,y,z,type,zopt){//"id",1d[],1d[],2d[]
  if(typeof(zopt)=="undefined")zopt = {type:"log"};
  type = typeof(type)!="undefined"?type:"heatmap";
  console.log("surf",type, zopt)
  var layout = {
    scene:{
      aspectmode: "manual",
      aspectratio: {
        x: 2, y: 1, z: 0.5,
      },
      camera:{
        projection:{
          type: "orthographic" 
        },
        ortho: true
      },
      xaxis: {autorange: "reversed"},
      yaxis: {autorange: "reversed"},
      zaxis: {type:zopt.type, autorange: true}//zopt
    }
  };
  //var data = [{x:x, y:y, z: z, type: 'surface'}];
  var data = [{x:x, y:y, z: z, colorscale: zopt.type=="log"?jetlog:'Jet', type: type}];
  return Plotly.newPlot(divId, data, layout);//returns promise
}

export function updateSurf(divId,x,y,z,zopt){//"id",1d[],1d[],2d[]
  var update = {
    x: [x],
    // y: [y],
    z: [z]
  };
  if(typeof(zopt)!="undefined" && typeof(zopt.type)!="undefined" && zopt.type=="log"){
    // let maxval = nj.max(spz);
    // update.c = colorize(ndarray(spz.slice().reverse().flat().map((e)=>Math.log(Number.isFinite(e)&&e>0?e:maxval*1e-5)),[spz.length,spz[0].length]).transpose(),{colormap:"jet",rgba:true,alpha:255}).data;//replace 0 values or NaN, convert to log jet colormap
  }
  return Plotly.update(divId, update);
}