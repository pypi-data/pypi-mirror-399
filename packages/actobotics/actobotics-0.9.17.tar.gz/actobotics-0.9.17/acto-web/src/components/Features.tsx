import { useState } from 'react';
import { motion } from 'framer-motion';
import { ScrollAnimation } from './ScrollAnimation';

const features = [
  {
    number: '01',
    title: 'Capture the moment',
    description: 'Every sensor reading. Every movement. Sealed with cryptographic signatures the moment it happens.',
    bgImage: '/bg1.png',
  },
  {
    number: '02',
    title: 'Trust no one',
    description: "Verification that doesn't rely on the operator's word. Anyone can check. No one can fake it.",
    bgImage: '/bg5.png',
  },
  {
    number: '03',
    title: 'Built for Web3',
    description: 'Your wallet is your identity. Token-gated access for committed users. Decentralized trust for autonomous machines.',
    bgImage: '/bg4.png',
  },
];

function FeatureCard({ feature, index }: { feature: typeof features[0]; index: number }) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <ScrollAnimation animation="blur-in" delay={index * 100}>
      <motion.div
        className="relative group cursor-default"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        initial={false}
      >
        {/* Background image on hover */}
        <motion.div
          className="absolute -inset-4 rounded-3xl overflow-hidden -z-10"
          animate={{ opacity: isHovered ? 1 : 0 }}
          transition={{ duration: 0.4 }}
        >
          <div 
            className="absolute inset-0 bg-cover bg-center"
            style={{ backgroundImage: `url(${feature.bgImage})` }}
          />
          <div className="absolute inset-0 bg-white/85" />
        </motion.div>
        
        {/* Subtle border */}
        <motion.div
          className="absolute -inset-4 rounded-3xl border border-neutral-200/50 opacity-0 -z-10"
          animate={{ opacity: isHovered ? 1 : 0 }}
          transition={{ duration: 0.3 }}
        />

        <div className="relative p-2">
          {/* Large number */}
          <motion.span
            className="block font-medium text-neutral-200 mb-4 select-none"
            animate={{ 
              fontSize: isHovered ? '48px' : '72px',
              color: isHovered ? 'rgb(163 163 163)' : 'rgb(229 229 229)',
            }}
            transition={{ duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
            style={{ lineHeight: 1 }}
          >
            {feature.number}
          </motion.span>

          {/* Title */}
          <motion.h3
            className="font-medium text-neutral-900 mb-3"
            animate={{ 
              fontSize: isHovered ? '24px' : '20px',
            }}
            transition={{ duration: 0.3 }}
          >
            {feature.title}
          </motion.h3>

          {/* Description - reveals on hover */}
          <motion.div
            className="overflow-hidden"
            initial={{ height: 0, opacity: 0 }}
            animate={{ 
              height: isHovered ? 'auto' : 0,
              opacity: isHovered ? 1 : 0,
            }}
            transition={{ duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
          >
            <p className="text-neutral-500 leading-relaxed pt-1">
              {feature.description}
            </p>
          </motion.div>

          {/* Minimal line indicator when collapsed */}
          <motion.div
            className="h-[2px] bg-neutral-200 mt-4 origin-left"
            animate={{ 
              scaleX: isHovered ? 0 : 1,
              opacity: isHovered ? 0 : 1,
            }}
            transition={{ duration: 0.3 }}
            style={{ width: '40px' }}
          />
        </div>
      </motion.div>
    </ScrollAnimation>
  );
}

export function Features() {
  return (
    <section className="border-t border-neutral-100">
      <div className="max-w-6xl mx-auto px-4 md:px-6 py-20 md:py-32">
        {/* Section hint */}
        <ScrollAnimation animation="blur-in" delay={0}>
          <p className="text-xs tracking-[0.3em] text-neutral-400 uppercase mb-16 md:mb-20">
            Why ACTO
          </p>
        </ScrollAnimation>

        <div className="grid md:grid-cols-3 gap-12 md:gap-16">
          {features.map((feature, index) => (
            <FeatureCard key={feature.number} feature={feature} index={index} />
          ))}
        </div>

        {/* Hint text */}
        <motion.p 
          className="text-center text-neutral-300 text-sm mt-16 md:mt-20"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          viewport={{ once: true }}
        >
          Hover to explore
        </motion.p>
      </div>
    </section>
  );
}
