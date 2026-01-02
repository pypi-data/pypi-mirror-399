import { useRef, useEffect, useState } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { Bot, Database, Shield, CheckCircle2 } from 'lucide-react';

const steps = [
  {
    number: '01',
    title: 'Robot executes task',
    description: 'Physical operation in the real world. The autonomous system performs its designated task while generating operational data.',
    icon: Bot,
  },
  {
    number: '02',
    title: 'Data collection',
    description: 'Telemetry and logs captured during execution. Sensor readings, timestamps, and action sequences are recorded.',
    icon: Database,
  },
  {
    number: '03',
    title: 'Proof generation',
    description: 'Deterministic cryptographic proof created. Ed25519 signatures seal the execution data into an immutable record.',
    icon: Shield,
  },
  {
    number: '04',
    title: 'Verification',
    description: 'Network-based proof verification. Anyone can independently verify the proof without trusting the operator.',
    icon: CheckCircle2,
  },
];

export function HowItWorks() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [activeStep, setActiveStep] = useState(0);
  
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"]
  });

  // Transform scroll progress to line height (0% to 100%)
  const lineHeight = useTransform(scrollYProgress, [0, 1], ["0%", "100%"]);
  
  // Update active step based on scroll
  useEffect(() => {
    const unsubscribe = scrollYProgress.on("change", (value) => {
      const stepIndex = Math.min(Math.floor(value * steps.length), steps.length - 1);
      setActiveStep(stepIndex);
    });
    return () => unsubscribe();
  }, [scrollYProgress]);

  return (
    <section 
      ref={containerRef}
      id="how-it-works-section"
      className="relative"
      style={{ height: `${(steps.length + 1) * 100}vh` }}
    >
      {/* Background image */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat bg-fixed"
        style={{ backgroundImage: 'url(/bg5.png)' }}
      />
      {/* Dark overlay */}
      <div className="absolute inset-0 bg-black/70" />
      
      {/* Sticky container */}
      <div className="sticky top-0 h-screen flex items-center overflow-hidden relative z-10">
        <div className="max-w-6xl mx-auto px-4 md:px-6 w-full">
          <div className="grid md:grid-cols-2 gap-12 md:gap-24">
            {/* Left side - Title (sticky) */}
            <div className="hidden md:flex flex-col justify-center">
              <motion.p 
                className="text-sm text-gray-500 mb-4 tracking-wide uppercase"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                The Process
              </motion.p>
              <motion.h2 
                className="text-3xl md:text-4xl lg:text-5xl font-medium mb-6 tracking-tight text-white"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 }}
              >
                How it works
              </motion.h2>
              <motion.p 
                className="text-gray-400 leading-relaxed max-w-md"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                Four steps from task execution to verifiable proof. 
                Each step builds on the previous, creating an unbroken chain of trust.
              </motion.p>
              
              {/* Progress indicator */}
              <div className="mt-12 flex items-center gap-3">
                <span className="text-4xl font-medium text-white">
                  {String(activeStep + 1).padStart(2, '0')}
                </span>
                <span className="text-gray-600">/</span>
                <span className="text-gray-600">
                  {String(steps.length).padStart(2, '0')}
                </span>
              </div>
            </div>

            {/* Right side - Steps with connecting line */}
            <div className="relative flex flex-col justify-center">
              {/* Mobile title */}
              <div className="md:hidden mb-8">
                <p className="text-sm text-gray-500 mb-2 tracking-wide uppercase">The Process</p>
                <h2 className="text-2xl font-medium mb-2 tracking-tight text-white">How it works</h2>
              </div>

              {/* Vertical line container */}
              <div className="absolute left-[19px] md:left-[23px] top-0 bottom-0 w-[2px] bg-neutral-800">
                {/* Animated fill */}
                <motion.div 
                  className="w-full bg-gradient-to-b from-white via-white to-gray-400 origin-top"
                  style={{ height: lineHeight }}
                />
              </div>

              {/* Steps */}
              <div className="space-y-12 md:space-y-16">
                {steps.map((step, index) => {
                  const Icon = step.icon;
                  const isActive = index <= activeStep;
                  
                  return (
                    <motion.div
                      key={step.number}
                      className="flex gap-6 md:gap-8 relative"
                      initial={{ opacity: 0.3 }}
                      animate={{ opacity: isActive ? 1 : 0.3 }}
                      transition={{ duration: 0.4 }}
                    >
                      {/* Step indicator dot */}
                      <div className="relative z-10 flex-shrink-0">
                        <motion.div 
                          className={`w-10 h-10 md:w-12 md:h-12 rounded-full flex items-center justify-center transition-colors duration-300 ${
                            isActive 
                              ? 'bg-white text-neutral-900' 
                              : 'bg-neutral-800 text-neutral-500'
                          }`}
                          animate={{ scale: isActive ? 1 : 0.9 }}
                          transition={{ duration: 0.3 }}
                        >
                          <Icon size={20} />
                        </motion.div>
                      </div>

                      {/* Content */}
                      <div className="pt-1 md:pt-2">
                        <p className={`text-xs font-medium mb-2 tracking-wider transition-colors duration-300 ${
                          isActive ? 'text-neutral-400' : 'text-neutral-600'
                        }`}>
                          STEP {step.number}
                        </p>
                        <h3 className={`text-lg md:text-xl font-medium mb-2 transition-colors duration-300 ${
                          isActive ? 'text-white' : 'text-neutral-600'
                        }`}>
                          {step.title}
                        </h3>
                        <p className={`text-sm leading-relaxed max-w-sm transition-colors duration-300 ${
                          isActive ? 'text-neutral-400' : 'text-neutral-700'
                        }`}>
                          {step.description}
                        </p>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
