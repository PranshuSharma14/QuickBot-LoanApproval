import React, { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Points, PointMaterial, Sphere } from '@react-three/drei'
import * as THREE from 'three'

function StarField(props) {
  const ref = useRef()
  const [sphere] = React.useState(() => new THREE.SphereGeometry(1, 32, 32))
  
  const points = useMemo(() => {
    const p = new Array(3000).fill(0).map(() => ({
      x: (Math.random() - 0.5) * 10,
      y: (Math.random() - 0.5) * 10,
      z: (Math.random() - 0.5) * 10,
    }))
    return p.map(({ x, y, z }) => new THREE.Vector3(x, y, z))
  }, [])

  useFrame((state, delta) => {
    if (ref.current) {
      ref.current.rotation.x -= delta / 10
      ref.current.rotation.y -= delta / 15
    }
  })

  return (
    <group rotation={[0, 0, Math.PI / 4]}>
      <Points ref={ref} positions={points} stride={3} frustumCulled={false} {...props}>
        <PointMaterial
          transparent
          color="#4f46e5"
          size={0.02}
          sizeAttenuation={true}
          depthWrite={false}
        />
      </Points>
    </group>
  )
}

function FloatingOrbs() {
  const orb1Ref = useRef()
  const orb2Ref = useRef()
  const orb3Ref = useRef()

  useFrame((state) => {
    const t = state.clock.getElapsedTime()
    
    if (orb1Ref.current) {
      orb1Ref.current.position.x = Math.sin(t * 0.3) * 2
      orb1Ref.current.position.y = Math.cos(t * 0.2) * 2
    }
    
    if (orb2Ref.current) {
      orb2Ref.current.position.x = Math.cos(t * 0.4) * 2.5
      orb2Ref.current.position.y = Math.sin(t * 0.3) * 2.5
    }
    
    if (orb3Ref.current) {
      orb3Ref.current.position.x = Math.sin(t * 0.2) * 3
      orb3Ref.current.position.y = Math.cos(t * 0.4) * 1.5
    }
  })

  return (
    <>
      <mesh ref={orb1Ref} position={[-2, 0, -5]}>
        <sphereGeometry args={[0.5, 32, 32]} />
        <meshStandardMaterial color="#818cf8" transparent opacity={0.3} />
      </mesh>
      <mesh ref={orb2Ref} position={[2, 0, -5]}>
        <sphereGeometry args={[0.7, 32, 32]} />
        <meshStandardMaterial color="#06b6d4" transparent opacity={0.3} />
      </mesh>
      <mesh ref={orb3Ref} position={[0, 2, -5]}>
        <sphereGeometry args={[0.6, 32, 32]} />
        <meshStandardMaterial color="#8b5cf6" transparent opacity={0.3} />
      </mesh>
    </>
  )
}

const AnimatedBackground = () => {
  return (
    <div className="fixed inset-0 -z-10">
      {/* Gradient Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900" />
      
      {/* Three.js Canvas */}
      <Canvas camera={{ position: [0, 0, 5] }} className="absolute inset-0">
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <StarField />
        <FloatingOrbs />
      </Canvas>
      
      {/* Overlay gradient for depth */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-slate-900/50" />
      
      {/* Animated gradient orbs */}
      <div className="absolute top-0 -left-4 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob" />
      <div className="absolute top-0 -right-4 w-72 h-72 bg-cyan-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000" />
      <div className="absolute -bottom-8 left-20 w-72 h-72 bg-indigo-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000" />
    </div>
  )
}

export default AnimatedBackground
