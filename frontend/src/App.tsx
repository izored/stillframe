import { AnimatePresence, motion } from "framer-motion";
import { Route, Routes, useLocation } from "react-router-dom";
import { pagePresence } from "./lib/motion";
import { DisclaimerBanner } from "./components/DisclaimerBanner";
import { Welcome } from "./screens/Welcome";
import { Home } from "./screens/Home";

export default function App() {
  const location = useLocation();
  return (
    <>
      <AnimatePresence mode="wait">
        <motion.div
          key={location.pathname}
          variants={pagePresence}
          initial="initial"
          animate="enter"
          exit="exit"
          style={{ minHeight: "100%" }}
        >
          <Routes location={location}>
            <Route path="/" element={<Welcome />} />
            <Route path="/home" element={<Home />} />
          </Routes>
        </motion.div>
      </AnimatePresence>
      <DisclaimerBanner />
    </>
  );
}
