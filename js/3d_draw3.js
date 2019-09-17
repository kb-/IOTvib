//Load 3d model in dom element
//3d orientation ok
import * as THREE from './three.js/build/three.module.js';

import Stats from './three.js/examples/jsm/libs/stats.module.js';

import { OrbitControls } from './three.js/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from './three.js/examples/jsm/loaders/GLTFLoader.js';
import { RGBELoader } from './three.js/examples/jsm/loaders/RGBELoader.js';
import { EquirectangularToCubeGenerator } from './three.js/examples/jsm/loaders/EquirectangularToCubeGenerator.js';
import { PMREMGenerator } from './three.js/examples/jsm/pmrem/PMREMGenerator.js';
import { PMREMCubeUVPacker } from './three.js/examples/jsm/pmrem/PMREMCubeUVPacker.js';

var container, stats, controls;
var camera, scene, renderer;
// init();
// animate();

export function init3d(elt, gltf_file) {

  container = document.createElement( 'div' );
  container.setAttribute("id", "graph3d");
  elt.appendChild( container );

  camera = new THREE.PerspectiveCamera( 45, elt.clientWidth / elt.clientHeight, 0.25, 20 );
  camera.position.set( - 1.8, 0.9, 2.7 );

  scene = new THREE.Scene();

  // model

  var loader = new GLTFLoader();
  loader.load(gltf_file, function ( gltf ) {

    scene.add( gltf.scene );

  },undefined,function(e){
    console.error(e);
  } );


  renderer = new THREE.WebGLRenderer( { antialias: true } );
  renderer.setPixelRatio( window.devicePixelRatio );
  renderer.setSize( elt.clientWidth, elt.clientHeight );
  renderer.gammaOutput = true;
  container.appendChild( renderer.domElement );

  controls = new OrbitControls( camera, renderer.domElement );
  controls.target.set( 0, - 0.2, - 0.2 );
  controls.update();

  window.addEventListener( 'resize', onWindowResize.bind(elt), false );//bind passes argument as cb's "this"

  // stats
  stats = new Stats();
  container.appendChild( stats.dom );
  return {scene:scene,THREE:THREE};
}

export function initSpectrogram(elt, shape) {

  container = document.createElement( 'div' );
  container.setAttribute("id", "Spectrogram");
  elt.appendChild( container );

  //camera = new THREE.PerspectiveCamera( 45, elt.clientWidth / elt.clientHeight, 0.25, 20 );
  var fov = 10;
  var near = 10;
  var far = 1000;
  camera = new THREE.PerspectiveCamera(fov, elt.clientWidth / elt.clientHeight, near, far + 1);

  camera.position.set( 0, 0, 600 );

  scene = new THREE.Scene();
  var directionalLight = new THREE.DirectionalLight( 0xffffff, 0.5 );
  scene.add( directionalLight );
  
  // model
  var geometry = new THREE.PlaneGeometry(120, 60, shape.x, shape.y);
  var material = new THREE.MeshBasicMaterial( {
    color: 0x0017c3, 
    side: THREE.DoubleSide, 
    vertexColors: THREE.VertexColors
  } );
  // var material = new THREE.MeshPhongMaterial({
    // color: 0xdddddd, 
    // wireframe: true
  // });
  var plane = new THREE.Mesh( geometry, material );
  plane.name = "Spectrogram";
  scene.add( plane );


  renderer = new THREE.WebGLRenderer( { antialias: true } );
  renderer.setPixelRatio( window.devicePixelRatio );
  renderer.setSize( elt.clientWidth, elt.clientHeight );
  renderer.gammaOutput = true;
  container.appendChild( renderer.domElement );

  controls = new OrbitControls( camera, renderer.domElement );
  controls.target.set( 0, 0, 0 );
  controls.update();

  window.addEventListener( 'resize', onWindowResize.bind(elt), false );//bind passes argument as cb's "this"

  // stats
  stats = new Stats();
  container.appendChild( stats.dom );
  return {scene:scene,THREE:THREE,controls:controls};
}

function onWindowResize() {

  camera.aspect = this.clientWidth / this.clientHeight;
  camera.updateProjectionMatrix();

  renderer.setSize( this.clientWidth, this.clientHeight );

}

//

export function animate3d() {

  requestAnimationFrame( animate3d );

  renderer.render( scene, camera );

  stats.update();

}