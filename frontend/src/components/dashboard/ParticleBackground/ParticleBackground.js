import { useMemo } from 'react';
import './ParticleBackground.css';

function ParticleBackground() {
  const particles = useMemo(() => {
    const particleArray = [];
    for (let i = 0; i < 100; i++) {
      particleArray.push({
        id: i,
        size: Math.random() * 3 + 1,
        left: Math.random() * 100,
        top: Math.random() * 100,
        blur: Math.random() * 1,
        duration: Math.random() * 40 + 10,
        delay: Math.random() * 2
      });
    }
    return particleArray;
  }, []); // Empty dependency array means it only generates once

  return (
    <>
      {particles.map(particle => (
        <div 
          key={particle.id}
          className="particle"
          style={{
            left: `${particle.left}%`,
            top: `${particle.top}%`,
            width: `${particle.size}px`,
            height: `${particle.size}px`,
            filter: `blur(${particle.blur}px)`,
            animationDuration: `${particle.duration}s`,
            animationDelay: `${particle.delay}s`
          }}
        />
      ))}
    </>
  );
}

export default ParticleBackground;

