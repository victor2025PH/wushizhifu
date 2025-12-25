import React, { useEffect, useRef } from 'react';

export const Celebration: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const particles: Particle[] = [];
    const colors = ['#C69C35', '#FCD34D', '#EF4444', '#DC2626', '#FFFFFF'];

    type ParticleType = 'confetti' | 'envelope';

    class Particle {
      x: number;
      y: number;
      vx: number;
      vy: number;
      color: string;
      size: number;
      rotation: number;
      rotationSpeed: number;
      type: ParticleType;
      
      constructor(x: number, y: number, type: ParticleType = 'confetti') {
        this.x = x;
        this.y = y;
        this.type = type;
        
        const angle = Math.random() * Math.PI * 2;
        // Explosion velocity
        const velocity = Math.random() * 15 + 5; 
        this.vx = Math.cos(angle) * velocity;
        this.vy = Math.sin(angle) * velocity - 5; // Initial upward kick
        
        this.color = colors[Math.floor(Math.random() * colors.length)];
        this.size = Math.random() * 8 + 4;
        if (type === 'envelope') this.size = 24; // Bigger envelopes
        
        this.rotation = Math.random() * 360;
        this.rotationSpeed = (Math.random() - 0.5) * 10;
      }

      update() {
        this.x += this.vx;
        this.y += this.vy;
        this.vy += 0.4; // Gravity
        this.vx *= 0.95; // Air resistance
        this.rotation += this.rotationSpeed;
      }

      draw(ctx: CanvasRenderingContext2D) {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate((this.rotation * Math.PI) / 180);
        
        if (this.type === 'envelope') {
          // Draw Red Envelope (Hongbao)
          const w = this.size;
          const h = this.size * 1.4;
          
          // Body
          ctx.fillStyle = '#DC2626'; 
          ctx.beginPath();
          // Use rect fallback if roundRect not supported in some envs, though modern browsers support it.
          if (ctx.roundRect) {
              ctx.roundRect(-w/2, -h/2, w, h, 2);
          } else {
              ctx.fillRect(-w/2, -h/2, w, h);
          }
          ctx.fill();
          
          // Flap/Gold accent
          ctx.fillStyle = '#FCD34D';
          ctx.beginPath();
          ctx.arc(0, -h/4, w/5, 0, Math.PI * 2);
          ctx.fill();
          
          // Gold line
          ctx.strokeStyle = '#FCD34D';
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(-w/2, -h/4);
          ctx.quadraticCurveTo(0, 0, w/2, -h/4);
          ctx.stroke();

        } else {
          // Standard Confetti
          ctx.fillStyle = this.color;
          ctx.fillRect(-this.size / 2, -this.size / 2, this.size, this.size * 1.5);
        }
        
        ctx.restore();
      }
    }

    // Spawn Particles function
    const spawnBatch = (x: number, y: number, count: number) => {
      for (let i = 0; i < count; i++) {
        const type = Math.random() > 0.85 ? 'envelope' : 'confetti';
        particles.push(new Particle(x, y, type));
      }
    };

    // 1. Center Explosion
    spawnBatch(canvas.width / 2, canvas.height / 2, 80);

    // 2. Side Cannons
    setTimeout(() => spawnBatch(0, canvas.height, 60), 200);
    setTimeout(() => spawnBatch(canvas.width, canvas.height, 60), 200);

    // 3. Rain from top
    const rainInterval = setInterval(() => {
       for(let i=0; i<5; i++) {
         const p = new Particle(Math.random() * canvas.width, -20, Math.random() > 0.7 ? 'envelope' : 'confetti');
         p.vy = Math.random() * 10 + 5; // Fast falling
         p.vx = (Math.random() - 0.5) * 2;
         particles.push(p);
       }
    }, 100);

    // Stop rain after 1.5s
    setTimeout(() => clearInterval(rainInterval), 1500);

    let animationId: number;
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        p.update();
        p.draw(ctx);
        
        if (p.y > canvas.height + 100) {
          particles.splice(i, 1);
        }
      }

      if (particles.length > 0) {
        animationId = requestAnimationFrame(animate);
      }
    };

    animate();

    return () => {
      cancelAnimationFrame(animationId);
      clearInterval(rainInterval);
    };
  }, []);

  return <canvas ref={canvasRef} className="fixed inset-0 z-[100] pointer-events-none" />;
};