import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Github, Menu, X } from 'lucide-react';
import { motion } from 'framer-motion';
import { config } from '../config';

// Animated nav link component with smooth underline
function NavLink({ to, children, onClick }: { to: string; children: React.ReactNode; onClick?: () => void }) {
  const [isHovered, setIsHovered] = useState(false);
  
  return (
    <Link 
      to={to} 
      onClick={onClick} 
      className="relative"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <span className={`text-sm transition-colors duration-200 whitespace-nowrap ${isHovered ? 'text-gray-900' : 'text-gray-500'}`}>
        {children}
      </span>
      <motion.span
        className="absolute -bottom-1 left-0 w-full h-[1px] bg-gray-900 origin-left"
        initial={{ scaleX: 0 }}
        animate={{ scaleX: isHovered ? 1 : 0 }}
        transition={{ duration: 0.25, ease: [0.25, 0.1, 0.25, 1] }}
      />
    </Link>
  );
}

function NavAnchor({ href, children }: { href: string; children: React.ReactNode }) {
  const [isHovered, setIsHovered] = useState(false);
  
  return (
    <a 
      href={href} 
      className="relative"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <span className={`text-sm transition-colors duration-200 whitespace-nowrap ${isHovered ? 'text-gray-900' : 'text-gray-500'}`}>
        {children}
      </span>
      <motion.span
        className="absolute -bottom-1 left-0 w-full h-[1px] bg-gray-900 origin-left"
        initial={{ scaleX: 0 }}
        animate={{ scaleX: isHovered ? 1 : 0 }}
        transition={{ duration: 0.25, ease: [0.25, 0.1, 0.25, 1] }}
      />
    </a>
  );
}

export function Navigation() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setMobileMenuOpen(true)}
        className="md:hidden fixed top-4 right-4 z-[60] p-2 bg-white/95 backdrop-blur-sm border border-gray-200 rounded-lg shadow-lg hover:bg-gray-50 transition-colors"
        aria-label="Open menu"
      >
        <Menu size={20} className="text-gray-900" />
      </button>

      {mobileMenuOpen && (
        <>
          <div
            className="md:hidden fixed inset-0 bg-black/50 z-[60] backdrop-blur-sm"
            onClick={() => setMobileMenuOpen(false)}
          />
          <div className="md:hidden fixed top-0 right-0 bottom-0 w-64 bg-white z-[60] shadow-2xl animate-slide-in">
            <div className="flex flex-col h-full">
              <div className="flex justify-end p-4 border-b border-gray-200">
                <button
                  onClick={() => setMobileMenuOpen(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  aria-label="Close menu"
                >
                  <X size={20} className="text-gray-900" />
                </button>
              </div>
              <nav className="flex flex-col p-6 gap-4">
                <Link
                  to="/"
                  className="text-base text-gray-700 hover:text-gray-900 transition-colors py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Home
                </Link>
                <Link
                  to="/about"
                  className="text-base text-gray-700 hover:text-gray-900 transition-colors py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  About
                </Link>
                <Link
                  to="/faq"
                  className="text-base text-gray-700 hover:text-gray-900 transition-colors py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  FAQ
                </Link>
                <Link
                  to="/comparison"
                  className="text-base text-gray-700 hover:text-gray-900 transition-colors py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Why ACTO?
                </Link>
                <a
                  href={config.links.docs}
                  className="text-base text-gray-700 hover:text-gray-900 transition-colors py-2"
                >
                  Docs
                </a>
                <a
                  href="https://api.actobotics.net/dashboard"
                  className="text-base text-gray-700 hover:text-gray-900 transition-colors py-2"
                >
                  Dashboard
                </a>
                <div className="flex gap-4 pt-4 border-t border-gray-200 mt-2">
                  <a
                    href={config.social.github}
                    className="text-gray-700 hover:text-gray-900 transition-colors"
                    aria-label="GitHub"
                  >
                    <Github size={20} />
                  </a>
                  <a
                    href={config.social.x}
                    className="text-gray-700 hover:text-gray-900 transition-colors"
                    aria-label="X"
                  >
                    <svg width="18" height="18" viewBox="0 0 1200 1227" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                      <path d="M714.163 519.284L1160.89 0H1055.03L667.137 450.887L357.328 0H0L468.492 681.821L0 1226.37H105.866L515.491 750.218L842.672 1226.37H1200L714.137 519.284H714.163ZM569.165 687.828L521.697 619.934L144.011 79.6944H306.615L611.412 515.685L658.88 583.579L1055.08 1150.3H892.476L569.165 687.854V687.828Z"/>
                    </svg>
                  </a>
                </div>
              </nav>
            </div>
          </div>
        </>
      )}

      <nav className="hidden md:block fixed top-0 left-1/2 -translate-x-1/2 z-50 group">
        <div className="flex flex-col items-center -translate-y-[calc(100%-28px)] group-hover:translate-y-0 transition-transform duration-300 ease-out">
          <div className="bg-white/95 backdrop-blur-sm border border-gray-200 border-t-0 rounded-b-lg shadow-lg px-8 py-4 flex items-center gap-8">
            <NavLink to="/">Home</NavLink>
            <NavLink to="/about">About</NavLink>
            <NavLink to="/faq">FAQ</NavLink>
            <NavLink to="/comparison">Why ACTO?</NavLink>
            <NavAnchor href={config.links.docs}>Docs</NavAnchor>
            <NavAnchor href="https://api.actobotics.net/dashboard">Dashboard</NavAnchor>
            <motion.a 
              href={config.social.github} 
              className="text-gray-500 hover:text-gray-900 transition-colors" 
              aria-label="GitHub"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            >
              <Github size={16} />
            </motion.a>
            <motion.a 
              href={config.social.x} 
              className="text-gray-500 hover:text-gray-900 transition-colors" 
              aria-label="X"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            >
              <svg width="14" height="14" viewBox="0 0 1200 1227" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                <path d="M714.163 519.284L1160.89 0H1055.03L667.137 450.887L357.328 0H0L468.492 681.821L0 1226.37H105.866L515.491 750.218L842.672 1226.37H1200L714.137 519.284H714.163ZM569.165 687.828L521.697 619.934L144.011 79.6944H306.615L611.412 515.685L658.88 583.579L1055.08 1150.3H892.476L569.165 687.854V687.828Z"/>
              </svg>
            </motion.a>
          </div>
          <div className="px-4 py-1.5 bg-gray-100 text-gray-500 text-xs font-medium rounded-b-lg cursor-default select-none">
            Pull me
          </div>
        </div>
      </nav>
    </>
  );
}
