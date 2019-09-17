//https://plot.ly/javascript/reference/#surface-hoverinfo//
//or
//https://plot.ly/javascript/reference/#surface-hovertemplate
//https://plot.ly/javascript/reference/#surface-colorbar-tickfont
//https://plot.ly/javascript/reference/#surface-colorbar-tickfont-size
//https://plot.ly/javascript/reference/#surface-colorscale
//https://plot.ly/javascript/reference/#surface-hoverlabel
//https://plot.ly/javascript/reference/#layout-scene-camera-projection
//https://plot.ly/javascript/reference/#layout-scene-aspectratio
//https://plot.ly/javascript/reference/#layout-scene-xaxis-title-text
//https://plot.ly/javascript/reference/#layout-scene-xaxis-type linear/log
//https://plot.ly/javascript/reference/#layout-scene-annotations-items-annotation-captureevents
//
//update
//https://plot.ly/javascript/plotlyjs-function-reference/#plotlynewplot

// import
//<script type="text/javascript" src="./plotly-latest.min.js" charset="utf-8"></script>
export function surf(x,y,z){
  var layout = {
    scene:{
      aspectmode: "manual",
      aspectratio: {
        x: 2, y: 1, z: 0.5,
      },
      camera:{
        projection:"orthographic"
      },
      zaxis: {
      }
    }
  }
  var data = [{x:x, y:y, z: z, type: 'surface'}];
  return Plotly.newPlot('Spectrogram', data);//returns promise
}

export function updateSurf(){
  
  
  
}