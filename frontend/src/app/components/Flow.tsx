"use client";

import React, { useCallback, useState } from "react";
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  BackgroundVariant,
  Panel,
  useOnSelectionChange,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import nodeTypes from "./nodes";
import { Button, Card, Space } from "antd";
import { TWorkerNode } from "./nodes/types";
import useAddWaterMarkToImages from "../hooks/apis/useAddWaterMarkToImages";

export default function WorkFlow() {
  const [nodes, setNodes, onNodesChange] = useNodesState<TWorkerNode[]>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  //
  const [selectedNodes, setSelectedNodes] = useState([]);
  const [selectedEdges, setSelectedEdges] = useState([]);

  // the passed handler has to be memoized, otherwise the hook will not work correctly
  const onChange = useCallback(({ nodes, edges }) => {
    setSelectedNodes(nodes.map((node: any) => node.id));
    setSelectedEdges(edges.map((edge: any) => edge.id));
  }, []);

  useOnSelectionChange({
    onChange,
  });

  const onConnect = useCallback(
    (params: any) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  return (
    <>
      <ReactFlow
        nodeTypes={nodeTypes}
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        proOptions={{ hideAttribution: true }}
        fitView
        colorMode="dark"
      >
        <Panel position="top-right">
          <Space>
            <Button onClick={() => {
              const newNode = { id: `${+new Date()}`, position: { x: 0, y: 0 }, data: { label: "1" }, type: "worker" };
              setNodes((nds) => [...nds, newNode]);
            }}>添加节点</Button>
            <Button>运行</Button>
          </Space>
        </Panel>
        <Controls />
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
      </ReactFlow>
      <Card style={{ position: "fixed", bottom: 20, right: 20 }}>
        {selectedNodes.length > 0 ? selectedNodes[0] : undefined}
      </Card>
    </>
  );
}
