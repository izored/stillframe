import type { Variants } from "framer-motion";

// Calm motion. Slower and softer than typical product UI.
export const calmEase: [number, number, number, number] = [0.22, 0.61, 0.36, 1];

export const fadeUp: Variants = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.7, ease: calmEase } },
};

export const stagger: Variants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.12, delayChildren: 0.1 } },
};

export const pagePresence: Variants = {
  initial: { opacity: 0 },
  enter: { opacity: 1, transition: { duration: 0.5, ease: calmEase } },
  exit: { opacity: 0, transition: { duration: 0.3, ease: calmEase } },
};

// System-wide press feedback (Apple discipline, calm).
export const pressTap = { scale: 0.97 };
