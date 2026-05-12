import React from 'react';

const AnimatedBackground: React.FC = () => {
  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      pointerEvents: 'none',
      zIndex: 0,
      overflow: 'hidden',
    }}>
      {/* Dot grid overlay */}
      <div style={{
        position: 'absolute',
        inset: 0,
        backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.06) 1px, transparent 1px)',
        backgroundSize: '32px 32px',
      }} />

      {/* Orb 1 — Blue */}
      <div style={{
        position: 'absolute',
        width: 600,
        height: 600,
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(10,132,255,0.15) 0%, transparent 70%)',
        top: -200,
        left: -200,
        animation: 'drift1 20s ease-in-out infinite alternate',
        filter: 'blur(1px)',
      }} />

      {/* Orb 2 — Purple */}
      <div style={{
        position: 'absolute',
        width: 500,
        height: 500,
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(191,90,242,0.12) 0%, transparent 70%)',
        top: '40%',
        right: -150,
        animation: 'drift2 25s ease-in-out infinite alternate',
        filter: 'blur(1px)',
      }} />

      {/* Orb 3 — Pink */}
      <div style={{
        position: 'absolute',
        width: 400,
        height: 400,
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(255,55,95,0.1) 0%, transparent 70%)',
        bottom: -100,
        left: '30%',
        animation: 'drift3 18s ease-in-out infinite alternate',
        filter: 'blur(1px)',
      }} />
    </div>
  );
};

export default AnimatedBackground;
