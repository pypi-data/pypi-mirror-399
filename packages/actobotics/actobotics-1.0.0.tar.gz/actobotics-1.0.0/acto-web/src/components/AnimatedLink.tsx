import { ReactNode } from 'react';
import { Link, LinkProps } from 'react-router-dom';
import { motion } from 'framer-motion';

interface AnimatedLinkProps extends Omit<LinkProps, 'className'> {
  children: ReactNode;
  className?: string;
  external?: boolean;
  href?: string;
}

// Wrapper component for smooth underline animation
export function AnimatedLink({ 
  children, 
  className = '', 
  external = false,
  href,
  ...props 
}: AnimatedLinkProps) {
  const underlineVariants = {
    initial: { scaleX: 0, originX: 0 },
    hover: { scaleX: 1, originX: 0 },
  };

  const content = (
    <motion.span
      className="relative inline-block"
      initial="initial"
      whileHover="hover"
    >
      {children}
      <motion.span
        className="absolute bottom-0 left-0 w-full h-[1px] bg-current"
        variants={underlineVariants}
        transition={{ duration: 0.3, ease: [0.25, 0.1, 0.25, 1] }}
      />
    </motion.span>
  );

  if (external && href) {
    return (
      <a 
        href={href} 
        className={className}
        target="_blank"
        rel="noopener noreferrer"
      >
        {content}
      </a>
    );
  }

  return (
    <Link className={className} {...props}>
      {content}
    </Link>
  );
}

// Simplified version for anchor tags (external links)
interface AnimatedAnchorProps {
  children: ReactNode;
  href: string;
  className?: string;
  ariaLabel?: string;
}

export function AnimatedAnchor({ 
  children, 
  href, 
  className = '',
  ariaLabel 
}: AnimatedAnchorProps) {
  const underlineVariants = {
    initial: { scaleX: 0, originX: 0 },
    hover: { scaleX: 1, originX: 0 },
  };

  return (
    <motion.a
      href={href}
      className={`relative inline-block ${className}`}
      initial="initial"
      whileHover="hover"
      aria-label={ariaLabel}
    >
      {children}
      <motion.span
        className="absolute bottom-0 left-0 w-full h-[1px] bg-current"
        variants={underlineVariants}
        transition={{ duration: 0.3, ease: [0.25, 0.1, 0.25, 1] }}
      />
    </motion.a>
  );
}

