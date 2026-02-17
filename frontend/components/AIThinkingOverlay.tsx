import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";

const defaultMessages = [
  "Analyzing market demand...",
  "Evaluating competition...",
  "Searching industry trends...",
  "Gathering salary data...",
  "Finalizing recommendations...",
];

interface AIThinkingOverlayProps {
  visible: boolean;
  onComplete: () => void;
  duration?: number;
  subtitle?: string;
  messages?: string[];
}

export default function AIThinkingOverlay({ visible, onComplete, duration = 10000, subtitle = "Searching", messages = defaultMessages }: AIThinkingOverlayProps) {
  const [msgIndex, setMsgIndex] = useState(0);

  useEffect(() => {
    if (!visible) { setMsgIndex(0); return; }

    const msgInterval = setInterval(() => {
      setMsgIndex((i) => (i + 1) % messages.length);
    }, 2000);

    const timer = setTimeout(() => {
      onComplete();
    }, duration);

    return () => { clearInterval(msgInterval); clearTimeout(timer); };
  }, [visible, onComplete, duration]);

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.5 }}
          className="fixed inset-0 z-[100] flex items-center justify-center"
          style={{ backdropFilter: "blur(12px)" }}
        >
          <div className="absolute inset-0 bg-black/90" />
          <div className="relative z-10 flex flex-col items-center gap-6">
            {/* Orb */}
            <div className="relative w-40 h-40">
              <div className="absolute inset-0 rounded-full" style={{
                background: "radial-gradient(circle at 30% 30%, hsl(183 100% 50% / 0.3), transparent)",
                filter: "blur(40px)"
              }} />
              <div className="absolute inset-4 rounded-full border border-cyan-400/30 animate-spin" style={{ animationDuration: "8s" }} />
              <div className="absolute inset-8 rounded-full border border-violet-400/20 animate-spin" style={{ animationDuration: "6s", animationDirection: "reverse" }} />
              <div className="absolute inset-12 rounded-full bg-cyan-400/10" />
              {/* Light trails */}
              {[0, 60, 120, 180, 240, 300].map((deg) => (
                <div
                  key={deg}
                  className="absolute top-1/2 left-1/2 w-1 h-16 -translate-x-1/2 origin-top"
                  style={{
                    transform: `rotate(${deg}deg) translateY(-70px)`,
                    background: `linear-gradient(to bottom, hsl(183 100% 50% / 0.4), transparent)`,
                    animation: `pulse 3s ease-in-out ${deg * 5}ms infinite`,
                  }}
                />
              ))}
            </div>

            {/* Subtitle */}
            <motion.p
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-3xl font-black text-cyan-400"
            >
              {subtitle}
            </motion.p>

            {/* Message */}
            <AnimatePresence mode="wait">
              <motion.p
                key={msgIndex}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
                className="text-sm font-medium text-white/60 text-center"
              >
                {messages[msgIndex]}
              </motion.p>
            </AnimatePresence>

            {/* Progress dots */}
            <div className="flex gap-2">
              {messages.map((_, i) => (
                <div
                  key={i}
                  className="w-2 h-2 rounded-full transition-all duration-300"
                  style={{
                    background: i <= msgIndex ? "hsl(183 100% 50%)" : "hsl(228 30% 22%)",
                    boxShadow: i <= msgIndex ? "0 0 8px hsl(183 100% 50% / 0.5)" : "none",
                  }}
                />
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
