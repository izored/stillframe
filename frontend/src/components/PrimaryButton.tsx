import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { pressTap } from "../lib/motion";

// The single Stillframe action: accent pill, calm press. One per screen.
export function PrimaryButton({
  children,
  onClick,
}: {
  children: ReactNode;
  onClick?: () => void;
}) {
  return (
    <motion.button
      whileTap={pressTap}
      onClick={onClick}
      style={{
        background: "var(--accent)",
        color: "#fff",
        borderRadius: "var(--radius-pill)",
        padding: "12px 26px",
        border: "none",
        fontFamily: "var(--font-sans)",
        fontSize: 17,
        cursor: "pointer",
      }}
    >
      {children}
    </motion.button>
  );
}
