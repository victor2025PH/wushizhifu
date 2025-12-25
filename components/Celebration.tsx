import React, { useEffect, useRef } from 'react';

export const Celebration: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Resize handler
    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', resize);
    resize();

    const particles: Particle[] = [];
    const colors = ['#C69C35', '#FCD34D', '#EF4444', '#DC2626', '#FFFFFF', '#FFD700'];

    type ParticleType = 'confetti' | 'envelope' | 'coin';

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
      opacity: number;
      
      constructor(x: number, y: number, type?: ParticleType) {
        this.x = x;
        this.y = y;
        
        // Randomize type if not provided
        if (type) {
            this.type = type;
        } else {
            const r = Math.random();
            if (r > 0.92) this.type = 'envelope';
            else if (r > 0.85) this.type = 'coin';
            else this.type = 'confetti';
        }

        const angle = Math.random() * Math.PI * 2;
        // Explosive velocity
        const velocity = Math.random() * 15 + 5; 
        
        this.vx = Math.cos(angle) * velocity;
        this.vy = Math.sin(angle) * velocity - 4; // Upward bias
        
        this.color = colors[Math.floor(Math.random() * colors.length)];
        
        if (this.type === 'envelope') {
            this.size = 28;
            this.vy -= 2; // Envelopes float a bit more
        } else if (this.type === 'coin') {
            this.size = 18;
        } else {
            this.size = Math.random() * 8 + 4;
        }
        
        this.rotation = Math.random() * 360;
        this.rotationSpeed = (Math.random() - 0.5) * 15;
        this.opacity = 1;
      }

      update() {
        this.x += this.vx;
        this.y += this.vy;
        this.vy += 0.3; // Gravity
        this.vx *= 0.95; // Drag
        this.vy *= 0.98; // Air resistance
        this.rotation += this.rotationSpeed;
        
        // Fade out
        if (this.opacity > 0) this.opacity -= 0.008;
      }

      draw(ctx: CanvasRenderingContext2D) {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate((this.rotation * Math.PI) / 180);
        ctx.globalAlpha = this.opacity;
        
        if (this.type === 'envelope') {
          // Draw Red Envelope (Hongbao)
          const w = this.size;
          const h = this.size * 1.4;
          
          // Body
          ctx.fillStyle = '#D32F2F'; // Rich Red
          ctx.beginPath();
          if ((ctx as any).roundRect) {
              (ctx as any).roundRect(-w/2, -h/2, w, h, 3);
          } else {
              ctx.fillRect(-w/2, -h/2, w, h);
          }
          ctx.fill();
          
          // Flap
          ctx.fillStyle = '#EF5350'; // Lighter Red
          ctx.beginPath();
          ctx.moveTo(-w/2, -h/4);
          ctx.quadraticCurveTo(0, h/5, w/2, -h/4);
          ctx.lineTo(w/2, -h/2);
          ctx.lineTo(-w/2, -h/2);
          ctx.closePath();
          ctx.fill();

          // Gold Seal
          ctx.fillStyle = '#FFD700';
          ctx.beginPath();
          ctx.arc(0, -h/8, w/7, 0, Math.PI * 2);
          ctx.fill();

        } else if (this.type === 'coin') {
           // Gold Coin
           const r = this.size / 2;
           ctx.beginPath();
           ctx.arc(0, 0, r, 0, Math.PI * 2);
           ctx.fillStyle = '#FFD700';
           ctx.fill();
           ctx.strokeStyle = '#DAA520';
           ctx.lineWidth = 2;
           ctx.stroke();

           // Inner square (ancient coin style)
           const s = r * 0.4;
           ctx.fillStyle = '#FFF8E1'; 
           ctx.fillRect(-s, -s, s*2, s*2);

        } else {
          // Confetti
          ctx.fillStyle = this.color;
          ctx.fillRect(-this.size / 2, -this.size / 2, this.size, this.size * 1.2);
        }
        
        ctx.restore();
      }
    }

    const spawnBurst = (x: number, y: number, count = 25) => {
        for (let i = 0; i < count; i++) {
            particles.push(new Particle(x, y));
        }
    }

    // Initial Celebration Sequence
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    
    // Series of bursts
    const timers: ReturnType<typeof setTimeout>[] = [];
    timers.push(setTimeout(() => spawnBurst(cx, cy + 100, 60), 0));
    timers.push(setTimeout(() => spawnBurst(cx - 100, cy, 40), 200));
    timers.push(setTimeout(() => spawnBurst(cx + 100, cy, 40), 400));
    timers.push(setTimeout(() => spawnBurst(cx, cy - 100, 50), 600));

    // Interaction Handlers
    const onClick = (e: MouseEvent) => {
        spawnBurst(e.clientX, e.clientY, 30);
    }
    const onTouch = (e: TouchEvent) => {
        // Prevent default to avoid double firing on some devices if they emulate mouse
        // e.preventDefault(); 
        const touch = e.touches[0];
        spawnBurst(touch.clientX, touch.clientY, 30);
    }

    // Add pointer events to canvas
    canvas.addEventListener('mousedown', onClick);
    canvas.addEventListener('touchstart', onTouch, { passive: true });

    let animationId: number;
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        p.update();
        p.draw(ctx);
        
        if (p.opacity <= 0 || p.y > canvas.height + 100) {
          particles.splice(i, 1);
        }
      }

      animationId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resize);
      canvas.removeEventListener('mousedown', onClick);
      canvas.removeEventListener('touchstart', onTouch);
      cancelAnimationFrame(animationId);
      timers.forEach(t => clearTimeout(t));
    };
  }, []);

  return <canvas ref={canvasRef} className="fixed inset-0 z-[100] cursor-pointer touch-none" />;
};