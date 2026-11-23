import React, { useEffect, useMemo } from 'react';
import * as THREE from 'three';
import { useFrame, useThree } from '@react-three/fiber';
import { DepthOfFieldShader, InkOutlineShader } from './shaders';

/**
 * Scene -> RT1 (colour + sharp depth) -> Pass 1 ink -> RT2 -> Pass 2 DoF (inked colour + RT1 depth) -> screen.
 * Ink must run before DoF (ANIMATION_GUIDE.md:390). Priority 1 takes over R3F's own render call.
 */
export const PostPipeline: React.FC<{ focusDist: number; inkColor: THREE.Color }> = ({ focusDist, inkColor }) => {
  const { gl, size } = useThree();
  const dpr = gl.getPixelRatio();
  const w = Math.round(size.width * dpr), h = Math.round(size.height * dpr);

  const { rt1, rt2, ink, dof, quad, orth } = useMemo(() => {
    const depthTexture = new THREE.DepthTexture(w, h);
    depthTexture.type = THREE.UnsignedIntType;
    const rt1 = new THREE.WebGLRenderTarget(w, h, { type: THREE.HalfFloatType, depthBuffer: true, depthTexture });
    const rt2 = new THREE.WebGLRenderTarget(w, h, { type: THREE.HalfFloatType, depthBuffer: false });
    const ink = new THREE.ShaderMaterial(InkOutlineShader());
    const dof = new THREE.ShaderMaterial(DepthOfFieldShader());
    const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2));
    quad.frustumCulled = false;
    return { rt1, rt2, ink, dof, quad, orth: new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1) };
  }, [w, h]);
  useEffect(() => () => { rt1.dispose(); rt2.dispose(); ink.dispose(); dof.dispose(); quad.geometry.dispose(); }, [rt1, rt2, ink, dof, quad]);

  useFrame(({ scene, camera }) => {
    const cam = camera as THREE.PerspectiveCamera;
    for (const m of [ink, dof]) {
      m.uniforms.tDepth.value = rt1.depthTexture;
      m.uniforms.uResolution.value.set(w, h);
      m.uniforms.uCameraNear.value = cam.near;
      m.uniforms.uCameraFar.value = cam.far;
    }
    ink.uniforms.tDiffuse.value = rt1.texture;
    ink.uniforms.uInkColor.value.copy(inkColor);
    dof.uniforms.tDiffuse.value = rt2.texture;
    dof.uniforms.uFocusDist.value = focusDist;

    gl.setRenderTarget(rt1);
    gl.render(scene, camera);
    quad.material = ink;
    gl.setRenderTarget(rt2);
    gl.render(quad, orth);
    quad.material = dof;
    gl.setRenderTarget(null);
    gl.render(quad, orth);
  }, 1);
  return null;
};
