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
export function surf(divId,x,y,z,type){//"id",1d[],1d[],2d[]
  type = typeof(type)!="undefined"?type:"heatmap";
  console.log("surf")
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
      zaxis: {
      }
    }
  }
  //var data = [{x:x, y:y, z: z, type: 'surface'}];
  var data = [{x:x, y:y, z: z, colorscale: 'Jet', type: type}];
  return Plotly.newPlot(divId, data, layout);//returns promise
}

export function updateSurf(divId,x,y,z){//"id",1d[],1d[],2d[]
  var update = {
    // x: [x],
    // y: [y],
    z: [z]
  }
  return Plotly.update(divId, update);
}