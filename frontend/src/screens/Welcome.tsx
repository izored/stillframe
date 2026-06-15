import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { fadeUp, stagger } from "../lib/motion";
import { PrimaryButton } from "../components/PrimaryButton";

export function Welcome() {
  const navigate = useNavigate();
  return (
    <motion.main
      variants={stagger}
      initial="hidden"
      animate="show"
      className="min-h-full flex flex-col items-center justify-center px-6 text-center"
    >
      <motion.h1
        variants={fadeUp}
        style={{ fontSize: 48, fontWeight: 600, letterSpacing: "-0.02em", margin: 0 }}
      >
        Stillframe
      </motion.h1>
      <motion.p
        variants={fadeUp}
        style={{ fontSize: 24, fontWeight: 300, color: "var(--ink-muted-80)", maxWidth: 460, marginTop: 18 }}
      >
        When life won't pause, your thoughts still can.
      </motion.p>
      <motion.p
        variants={fadeUp}
        style={{ fontSize: 17, color: "var(--ink-muted-48)", maxWidth: 420, marginTop: 12 }}
      >
        Frame one moment, sit with it safely, and move on a little lighter.
      </motion.p>
      <motion.div variants={fadeUp} style={{ marginTop: 36 }}>
        <PrimaryButton onClick={() => navigate("/home")}>Begin</PrimaryButton>
      </motion.div>
    </motion.main>
  );
}
