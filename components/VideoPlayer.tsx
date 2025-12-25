import React, { useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { X, Play, Pause, Volume2, VolumeX, Maximize } from 'lucide-react';

interface VideoPlayerProps {
  videoSrc: string;
  onClose: () => void;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({ videoSrc, onClose }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const toggleFullscreen = () => {
    if (videoRef.current) {
      if (!document.fullscreenElement) {
        videoRef.current.requestFullscreen().then(() => {
          setIsFullscreen(true);
        });
      } else {
        document.exitFullscreen().then(() => {
          setIsFullscreen(false);
        });
      }
    }
  };

  const handleVideoClick = () => {
    togglePlay();
  };

  return (
    <div className="relative w-full bg-black rounded-2xl overflow-hidden aspect-video">
      {/* Close Button */}
      <button
        onClick={onClose}
        className="absolute top-2 right-2 z-20 p-2 bg-black/60 hover:bg-black/80 rounded-full transition-colors"
        aria-label="Close"
      >
        <X className="w-5 h-5 text-white" />
      </button>

      {/* Video Element */}
      <video
        ref={videoRef}
        src={videoSrc}
        className="w-full h-full object-contain cursor-pointer"
        onClick={handleVideoClick}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onEnded={() => setIsPlaying(false)}
      />

      {/* Controls Overlay */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
        <div className="flex items-center justify-center space-x-4">
          {/* Play/Pause Button */}
          <button
            onClick={togglePlay}
            className="p-2 bg-white/20 hover:bg-white/30 rounded-full transition-colors"
            aria-label={isPlaying ? 'Pause' : 'Play'}
          >
            {isPlaying ? (
              <Pause className="w-6 h-6 text-white" />
            ) : (
              <Play className="w-6 h-6 text-white" />
            )}
          </button>

          {/* Mute/Unmute Button */}
          <button
            onClick={toggleMute}
            className="p-2 bg-white/20 hover:bg-white/30 rounded-full transition-colors"
            aria-label={isMuted ? 'Unmute' : 'Mute'}
          >
            {isMuted ? (
              <VolumeX className="w-5 h-5 text-white" />
            ) : (
              <Volume2 className="w-5 h-5 text-white" />
            )}
          </button>

          {/* Fullscreen Button */}
          <button
            onClick={toggleFullscreen}
            className="p-2 bg-white/20 hover:bg-white/30 rounded-full transition-colors"
            aria-label="Fullscreen"
          >
            <Maximize className="w-5 h-5 text-white" />
          </button>
        </div>
      </div>
    </div>
  );
};

