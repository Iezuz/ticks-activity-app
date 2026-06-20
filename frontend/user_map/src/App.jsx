import { Routes, Route } from "react-router-dom";

import HomePage from "./pages/MapPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<MapPage />} />
    </Routes>
  );
}