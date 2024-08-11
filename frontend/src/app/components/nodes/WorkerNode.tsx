import { Handle, Position } from "@xyflow/react";
import { Card } from "antd";
import { FC } from "react";

const WorkerNode: FC = () => {
  return (
    <>
      <Card>test</Card>
      <Handle type="source" position={Position.Left} />
      <Handle type="target" position={Position.Right} />
    </>
  );
};

export default WorkerNode;
