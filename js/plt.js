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
// var jet = colormap({nshades:6,colormap:"jet",format:"rgb"});
// var idx = arraytools.linspace(5,0,6).map(e=>1/Math.pow(10,e));
// idx[0] = 0;
// var jetlog = jet.map((e,i)=>({index:idx[i], rgb:e.slice(0,3)}));

var logbinslog = arraytools.linspace(-10,10,21);
var logbins = arraytools.linspace(-10,10,21).map((e)=>Math.pow(10,e).toExponential());//exponential notation 1e-10:->1e10

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
      zaxis: {autorange: true,
        // tickvals:arraytools.linspace(-10,10,21),
        // ticktext:arraytools.linspace(-10,10,21).map((e)=>Math.pow(10,e).toExponential())//exponential notation 1e-10:->1e10
      }//zopt
    }
  };
  //var data = [{x:x, y:y, z: z, type: 'surface'}];
  var data = {x:x, y:y, z: z, colorscale:'Jet', type: type, hoverinfo: 'none'};
  var maxval = nj.max(spz);
  var minval = nj.min(spz);
  if(zopt.type=="log"){
    data.z = math.matrix(z).map((e,i,m)=>e==0?Math.log10(maxval)-5:math.log10(e)).toArray();//log10 z data
    layout.scene.zaxis.tickvals = logbinslog;
    layout.scene.zaxis.ticktext = logbins;
    data.colorbar = colorbar(minval, maxval);
    // data.colorbar = {
      // tickvals: logbinslog.concat([(Math.log10(minval)), (Math.log10(maxval))]),
      // ticktext: logbins.concat([minval.toExponential(3), maxval.toExponential(3)]),
    // };
  }
  
  
  return Plotly.newPlot(divId, [data], layout);//returns promise
}

export function updateSurf(divId,x,y,z,zopt){//"id",1d[],1d[],2d[]
  var maxval = nj.max(spz);
  var minval = nj.min(spz);
  var update = {
    x: [x],
    // y: [y],
    z: [z],
  };
  
  update.colorbar={};//reset colorbar (for lin/log toggle)
  if(typeof(zopt)!="undefined" && typeof(zopt.type)!="undefined" && zopt.type=="log"){
    update.z = [math.matrix(z).map((e,i,m)=>e==0?Math.log10(maxval)-5:math.log10(e)).toArray()];
    // let maxval = nj.max(spz);
    // update.c = colorize(ndarray(spz.slice().reverse().flat().map((e)=>Math.log(Number.isFinite(e)&&e>0?e:maxval*1e-5)),[spz.length,spz[0].length]).transpose(),{colormap:"jet",rgba:true,alpha:255}).data;//replace 0 values or NaN, convert to log jet colormap
    update.colorbar = colorbar(minval, maxval);
    // update.colorbar = {
      // tickvals: logbinslog.concat([(Math.log10(minval)), (Math.log10(maxval))]),
      // ticktext: logbins.concat([minval.toExponential(3), maxval.toExponential(3)]),
    // }
  }
  return Plotly.update(divId, update);
}

function colorbar(minval, maxval){
  var minbin = logbinslog.findIndex((e)=>e==Math.round(Math.log10(minval)));
  var maxbin = logbinslog.findIndex((e)=>e==Math.round(Math.log10(maxval)));
  var colorbar = {
    tickvals: logbinslog.concat([(Math.log10(minval)), (Math.log10(maxval))]).filter((e,i)=>(i != minbin && i != maxbin)),
    ticktext: logbins.concat([minval.toExponential(3), maxval.toExponential(3)]).filter((e,i)=>(i != minbin && i != maxbin)),
  }
  
  return colorbar;
}