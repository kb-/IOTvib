var createScene       = require('gl-plot3d').createScene
var createSurfacePlot = require('gl-surface3d')
var ndarray           = require('ndarray')
var fill              = require('ndarray-fill')
var diric             = require('dirichlet')

window.createScene = createScene;
window.createSurfacePlot = createSurfacePlot;
window.ndarray = ndarray;
window.fill = fill;
window.diric = diric;