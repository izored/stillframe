import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { fadeUp, stagger } from "../lib/motion";
import { PrimaryButton } from "../components/PrimaryButton";
import { api, type ProviderInfo } from "../lib/api";

export function Home() {
  const [editor, setEditor] = useState<string>("checking your editor...");

  useEffect(() => {
    api
      .providers()
      .then(({ data }) => {
        const active = data.find((p: ProviderInfo) => p.available) ?? data[0];
        setEditor(
          active?.available
            ? `${active.label}${active.default_model ? ` · ${active.default_model}` : ""}`
            : "No editor reachable yet"
        );
      })
      .catch(() => setEditor("Backend not reachable"));
  }, []);

  return (
    <motion.main
      variants={stagger}
      initial="hidden"
      animate="show"
      className="min-h-full flex flex-col items-center justify-center px-6 text-center"
    >
      <motion.p variants={fadeUp} style={{ fontSize: 17, color: "var(--ink-muted-48)", margin: 0 }}>
        Good to see you. What's on your mind?
      </motion.p>
      <motion.div variants={fadeUp} style={{ marginTop: 28 }}>
        <PrimaryButton>Frame a thought</PrimaryButton>
      </motion.div>
      <motion.p
        variants={fadeUp}
        style={{ fontSize: 12, color: "var(--ink-muted-48)", marginTop: 40 }}
      >
        Editor: {editor}
      </motion.p>
    </motion.main>
  );
}
