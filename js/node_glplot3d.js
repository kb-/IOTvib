var createScene       = require('gl-plot3d').createScene
var createSurfacePlot = require('gl-surface3d')
var ndarray           = require('ndarray')
var fill              = require('ndarray-fill')
var diric             = require('dirichlet')
 
var scene = createScene()
 
var field = ndarray(new Float32Array(512*512), [512,512])
fill(field, function(x,y) {
  return 128 * diric(10, 10.0*(x-256)/512) * diric(10, 10.0*(y-256)/512)
})
 
var surface = createSurfacePlot({
  gl:             scene.gl,
  field:          field,
  contourProject: true
})
 
scene.add(surface)