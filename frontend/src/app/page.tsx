"use client";

import React from "react";
import WorkFlow from "./components/Flow";
import { ReactFlowProvider } from "@xyflow/react";

export default function App() {
  return (
    <ReactFlowProvider>
      <WorkFlow />
    </ReactFlowProvider>
  );
}
