import { useRef } from 'react';
import { motion, useInView } from 'framer-motion';

interface TextRevealProps {
  children: string;
  className?: string;
  delay?: number;
  staggerDelay?: number;
  once?: boolean;
}

/**
 * TextReveal - Animates text line by line or word by word
 * 
 * Usage:
 * <TextReveal>Your text here that will animate line by line</TextReveal>
 */
export function TextReveal({ 
  children, 
  className = '', 
  delay = 0,
  staggerDelay = 0.08,
  once = true
}: TextRevealProps) {
  const ref = useRef<HTMLSpanElement>(null);
  const isInView = useInView(ref, { once, margin: "-50px" });

  // Split text into words
  const words = children.split(' ');

  const containerVariants = {
    hidden: {},
    visible: {
      transition: {
        staggerChildren: staggerDelay,
        delayChildren: delay / 1000,
      },
    },
  };

  const wordVariants = {
    hidden: { 
      opacity: 0, 
      y: 20,
      filter: 'blur(4px)',
    },
    visible: { 
      opacity: 1, 
      y: 0,
      filter: 'blur(0px)',
      transition: {
        duration: 0.5,
        ease: "easeOut" as const,
      },
    },
  };

  return (
    <motion.span
      ref={ref}
      className={`inline ${className}`}
      variants={containerVariants}
      initial="hidden"
      animate={isInView ? "visible" : "hidden"}
    >
      {words.map((word, index) => (
        <motion.span
          key={index}
          variants={wordVariants}
          className="inline-block"
        >
          {word}
          {index < words.length - 1 && <span>&nbsp;</span>}
        </motion.span>
      ))}
    </motion.span>
  );
}

interface LineRevealProps {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  once?: boolean;
}

/**
 * LineReveal - Animates a single line/element with slide-up and fade
 */
export function LineReveal({ 
  children, 
  className = '', 
  delay = 0,
  once = true
}: LineRevealProps) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once, margin: "-50px" });

  return (
    <div ref={ref} className={`overflow-hidden pb-[0.15em] ${className}`}>
      <motion.div
        initial={{ opacity: 0, y: '100%' }}
        animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: '100%' }}
        transition={{
          duration: 0.6,
          delay: delay / 1000,
          ease: [0.25, 0.1, 0.25, 1],
        }}
      >
        {children}
      </motion.div>
    </div>
  );
}

interface SplitLineRevealProps {
  children: string;
  className?: string;
  lineClassName?: string;
  delay?: number;
  staggerDelay?: number;
  once?: boolean;
}

/**
 * SplitLineReveal - Splits text by <br /> and animates each line
 */
export function SplitLineReveal({ 
  children, 
  className = '',
  lineClassName = '',
  delay = 0,
  staggerDelay = 0.1,
  once = true
}: SplitLineRevealProps) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once, margin: "-50px" });

  // Split by newlines or <br>
  const lines = children.split(/\n|<br\s*\/?>/);

  return (
    <div ref={ref} className={className}>
      {lines.map((line, index) => (
        <div key={index} className="overflow-hidden">
          <motion.div
            className={lineClassName}
            initial={{ opacity: 0, y: '100%' }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: '100%' }}
            transition={{
              duration: 0.6,
              delay: (delay / 1000) + (index * staggerDelay),
              ease: [0.25, 0.1, 0.25, 1],
            }}
          >
            {line}
          </motion.div>
        </div>
      ))}
    </div>
  );
}

