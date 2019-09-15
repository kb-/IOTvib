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

export function init3d(elt) {

  container = document.createElement( 'div' );
  container.setAttribute("id", "graph3d");
  elt.appendChild( container );

  camera = new THREE.PerspectiveCamera( 45, elt.clientWidth / elt.clientHeight, 0.25, 20 );
  camera.position.set( - 1.8, 0.9, 2.7 );

  scene = new THREE.Scene();

  new RGBELoader()
    .setDataType( THREE.UnsignedByteType )
    .setPath( '/js/three.js/examples/textures/equirectangular/' )
    .load( 'pedestrian_overpass_2k.hdr', function ( texture ) {

      var cubeGenerator = new EquirectangularToCubeGenerator( texture, { resolution: 1024 } );
      cubeGenerator.update( renderer );

      var pmremGenerator = new PMREMGenerator( cubeGenerator.renderTarget.texture );
      pmremGenerator.update( renderer );

      var pmremCubeUVPacker = new PMREMCubeUVPacker( pmremGenerator.cubeLods );
      pmremCubeUVPacker.update( renderer );

      var envMap = pmremCubeUVPacker.CubeUVRenderTarget.texture;

      // model

      var loader = new GLTFLoader().setPath( '/js/three.js/examples/models/gltf/DamagedHelmet/glTF/' );
      loader.load( 'DamagedHelmet.gltf', function ( gltf ) {

        gltf.scene.traverse( function ( child ) {

          if ( child.isMesh ) {

            child.material.envMap = envMap;

          }

        } );

        scene.add( gltf.scene );

      } );

      pmremGenerator.dispose();
      pmremCubeUVPacker.dispose();

      scene.background = cubeGenerator.renderTarget;

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