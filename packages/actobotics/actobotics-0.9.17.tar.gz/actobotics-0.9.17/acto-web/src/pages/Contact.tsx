import { useState, useEffect, useRef, FormEvent } from 'react';
import { ArrowRight, ArrowUpRight, Copy, Check, CheckCircle2, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { config } from '../config';
import { SEO } from '../components/SEO';
import { ScrollAnimation } from '../components/ScrollAnimation';

// Web3Forms Access Key - set via environment variable in Vercel
const WEB3FORMS_KEY = import.meta.env.VITE_WEB3FORMS_KEY;
// Web3Forms hCaptcha Sitekey
const HCAPTCHA_SITEKEY = '50b2fe65-b00b-4b9e-ad62-3ba471098be2';

// Extend window for hcaptcha
declare global {
  interface Window {
    hcaptcha?: {
      reset: (widgetId?: string) => void;
    };
  }
}

export function Contact() {
  const [copied, setCopied] = useState(false);
  const [formState, setFormState] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle');
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: '',
  });
  const formRef = useRef<HTMLFormElement>(null);

  // Load hCaptcha script
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://web3forms.com/client/script.js';
    script.async = true;
    script.defer = true;
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, []);

  const copyEmail = () => {
    navigator.clipboard.writeText('info@actobotics.net');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setFormState('submitting');

    try {
      const form = formRef.current;
      if (!form) return;

      const formDataObj = new FormData(form);
      formDataObj.append('access_key', WEB3FORMS_KEY);
      formDataObj.append('subject', `[ACTO Contact] Message from ${formData.name}`);

      const response = await fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        body: formDataObj,
      });

      const data = await response.json();

      if (data.success) {
        setFormState('success');
        setFormData({ name: '', email: '', message: '' });
        // Reset hCaptcha
        if (window.hcaptcha) {
          window.hcaptcha.reset();
        }
      } else {
        setFormState('error');
      }
    } catch {
      setFormState('error');
    }
  };

  return (
    <>
      <SEO
        title="Contact — ACTO"
        description="Questions about proof-of-execution? Partnership inquiries? Drop us a line."
        url="https://actobotics.net/contact"
      />
      
      <div className="min-h-screen bg-white">
        {/* Hero - Full viewport height with centered content */}
        <section id="contact-hero" className="min-h-screen flex items-center relative overflow-hidden">
          {/* Background image */}
          <div 
            className="absolute inset-0 bg-cover bg-center bg-no-repeat"
            style={{ backgroundImage: 'url(/bg6.png)' }}
          />
          <div className="absolute inset-0 bg-gradient-to-b from-white/70 via-white/40 to-white" />
          
          <div className="max-w-7xl mx-auto px-4 md:px-6 w-full py-32">
            <div className="grid lg:grid-cols-2 gap-16 lg:gap-24 items-center">
              {/* Left - Big Typography */}
              <div>
                <ScrollAnimation animation="blur-in" delay={0}>
                  <p className="text-xs tracking-[0.3em] text-neutral-600 uppercase mb-8">
                    Get in touch
                  </p>
                </ScrollAnimation>
                
                <ScrollAnimation animation="blur-in" delay={100}>
                  <h1 className="text-5xl md:text-6xl lg:text-7xl font-medium tracking-tight leading-[0.95] mb-8 text-neutral-900">
                    Let's build<br />
                    <span className="text-neutral-500">something</span><br />
                    together.
                  </h1>
                </ScrollAnimation>
                
                <ScrollAnimation animation="blur-in" delay={200}>
                  <p className="text-lg text-neutral-700 max-w-md leading-relaxed mb-12">
                    Whether you're integrating proof-of-execution into your robotics fleet 
                    or just curious about cryptographic verification — we'd love to hear from you.
                  </p>
                </ScrollAnimation>

                {/* Email - Click to copy or open */}
                <ScrollAnimation animation="blur-in" delay={300}>
                  <div className="inline-block">
                    <p className="text-xs tracking-[0.2em] text-neutral-600 uppercase mb-3">Email us directly</p>
                    <div className="flex items-center gap-4">
                      <a 
                        href="mailto:info@actobotics.net"
                        className="group text-2xl md:text-3xl font-medium text-neutral-900 hover:text-neutral-600 transition-colors"
                      >
                        info@actobotics.net
                        <span className="inline-block ml-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <ArrowUpRight className="w-5 h-5 inline" />
                        </span>
                      </a>
                      <button
                        onClick={copyEmail}
                        className="p-2 text-neutral-600 hover:text-neutral-900 hover:bg-neutral-200/50 rounded-lg transition-all"
                        aria-label="Copy email"
                      >
                        {copied ? <Check className="w-5 h-5" /> : <Copy className="w-5 h-5" />}
                      </button>
                    </div>
                    {copied && (
                      <motion.p 
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-sm text-neutral-700 mt-2"
                      >
                        Copied to clipboard
                      </motion.p>
                    )}
                  </div>
                </ScrollAnimation>
              </div>

              {/* Right - Minimal Form */}
              <ScrollAnimation animation="blur-in" delay={400}>
                <div className="relative">
                  {/* Decorative corner brackets */}
                  <div className="absolute -top-4 -left-4 w-8 h-8 border-l-2 border-t-2 border-neutral-300" />
                  <div className="absolute -bottom-4 -right-4 w-8 h-8 border-r-2 border-b-2 border-neutral-300" />
                  
                  <AnimatePresence mode="wait">
                    {formState === 'success' ? (
                      <motion.div 
                        key="success"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="p-8 md:p-12 text-center"
                      >
                        <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center mx-auto mb-6">
                          <CheckCircle2 className="w-8 h-8 text-neutral-900" />
                        </div>
                        <h3 className="text-2xl font-medium text-neutral-900 mb-3">Message sent!</h3>
                        <p className="text-neutral-600 mb-8">We'll get back to you as soon as possible.</p>
                        <button
                          onClick={() => setFormState('idle')}
                          className="text-sm tracking-wide uppercase text-neutral-900 hover:text-neutral-600 transition-colors"
                        >
                          Send another message
                        </button>
                      </motion.div>
                    ) : (
                      <motion.form 
                        key="form"
                        ref={formRef}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onSubmit={handleSubmit} 
                        className="space-y-8 p-8 md:p-12"
                      >
                        <div>
                          <label className="block text-xs tracking-[0.2em] text-neutral-600 uppercase mb-3">
                            Your name
                          </label>
                          <input
                            type="text"
                            name="name"
                            required
                            disabled={formState === 'submitting'}
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            className="w-full bg-transparent border-b-2 border-neutral-300 py-3 text-lg text-neutral-900 focus:outline-none focus:border-neutral-900 transition-colors placeholder:text-neutral-400 disabled:opacity-50"
                            placeholder="Jane Doe"
                          />
                        </div>
                        
                        <div>
                          <label className="block text-xs tracking-[0.2em] text-neutral-600 uppercase mb-3">
                            Your email
                          </label>
                          <input
                            type="email"
                            name="email"
                            required
                            disabled={formState === 'submitting'}
                            value={formData.email}
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            className="w-full bg-transparent border-b-2 border-neutral-300 py-3 text-lg text-neutral-900 focus:outline-none focus:border-neutral-900 transition-colors placeholder:text-neutral-400 disabled:opacity-50"
                            placeholder="jane@company.com"
                          />
                        </div>
                        
                        <div>
                          <label className="block text-xs tracking-[0.2em] text-neutral-600 uppercase mb-3">
                            Message
                          </label>
                          <textarea
                            name="message"
                            required
                            rows={4}
                            disabled={formState === 'submitting'}
                            value={formData.message}
                            onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                            className="w-full bg-transparent border-b-2 border-neutral-300 py-3 text-lg text-neutral-900 focus:outline-none focus:border-neutral-900 transition-colors resize-none placeholder:text-neutral-400 disabled:opacity-50"
                            placeholder="Tell us about your project..."
                          />
                        </div>

                        {formState === 'error' && (
                          <motion.div 
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="flex items-center gap-3 text-red-600"
                          >
                            <AlertCircle className="w-5 h-5 flex-shrink-0" />
                            <p className="text-sm">Something went wrong. Please try again.</p>
                          </motion.div>
                        )}

                        {/* hCaptcha Widget */}
                        <div 
                          className="h-captcha" 
                          data-captcha="true"
                          data-sitekey={HCAPTCHA_SITEKEY}
                        />

                        <button
                          type="submit"
                          disabled={formState === 'submitting'}
                          className="group w-full flex items-center justify-between px-6 py-4 bg-neutral-900 text-white rounded-none hover:bg-neutral-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {formState === 'submitting' ? (
                            <>
                              <span className="text-sm tracking-wide uppercase">Sending...</span>
                              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            </>
                          ) : (
                            <>
                              <span className="text-sm tracking-wide uppercase">Send Message</span>
                              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                            </>
                          )}
                        </button>
                      </motion.form>
                    )}
                  </AnimatePresence>
                </div>
              </ScrollAnimation>
            </div>
          </div>
        </section>

        {/* Social Links Section */}
        <section>
          <div className="max-w-7xl mx-auto">
            <div className="grid md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-neutral-100">
              {/* GitHub */}
              <ScrollAnimation animation="blur-in" delay={0}>
                <a 
                  href={config.social.github}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group flex items-center justify-between p-8 md:p-12 hover:bg-neutral-50 transition-colors"
                >
                  <div>
                    <p className="text-xs tracking-[0.2em] text-neutral-500 uppercase mb-2">Open Source</p>
                    <p className="text-xl font-medium text-neutral-900 group-hover:text-neutral-600 transition-colors">GitHub</p>
                  </div>
                  <ArrowUpRight className="w-6 h-6 text-neutral-400 group-hover:text-neutral-900 group-hover:translate-x-1 group-hover:-translate-y-1 transition-all" />
                </a>
              </ScrollAnimation>
              
              {/* X / Twitter */}
              <ScrollAnimation animation="blur-in" delay={100}>
                <a 
                  href={config.social.x}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group flex items-center justify-between p-8 md:p-12 hover:bg-neutral-50 transition-colors"
                >
                  <div>
                    <p className="text-xs tracking-[0.2em] text-neutral-500 uppercase mb-2">Updates</p>
                    <p className="text-xl font-medium text-neutral-900 group-hover:text-neutral-600 transition-colors">X (Twitter)</p>
                  </div>
                  <ArrowUpRight className="w-6 h-6 text-neutral-400 group-hover:text-neutral-900 group-hover:translate-x-1 group-hover:-translate-y-1 transition-all" />
                </a>
              </ScrollAnimation>
              
              {/* Docs */}
              <ScrollAnimation animation="blur-in" delay={200}>
                <a 
                  href={config.links.docs}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group flex items-center justify-between p-8 md:p-12 hover:bg-neutral-50 transition-colors"
                >
                  <div>
                    <p className="text-xs tracking-[0.2em] text-neutral-500 uppercase mb-2">Learn More</p>
                    <p className="text-xl font-medium text-neutral-900 group-hover:text-neutral-600 transition-colors">Documentation</p>
                  </div>
                  <ArrowUpRight className="w-6 h-6 text-neutral-400 group-hover:text-neutral-900 group-hover:translate-x-1 group-hover:-translate-y-1 transition-all" />
                </a>
              </ScrollAnimation>
            </div>
          </div>
        </section>

        {/* Bottom text */}
        <section className="py-24 md:py-32">
          <div className="max-w-7xl mx-auto px-4 md:px-6 text-center">
            <ScrollAnimation animation="blur-in" delay={0}>
              <p className="text-neutral-600 max-w-lg mx-auto leading-relaxed">
                We typically respond within 24 hours. For urgent matters 
                regarding API access or technical issues, please use 
                the <a href={config.links.dashboard} className="text-neutral-900 hover:underline">dashboard</a>.
              </p>
            </ScrollAnimation>
          </div>
        </section>
      </div>
    </>
  );
}
