import { Handle, NodeProps, Position } from "@xyflow/react";
import { Card } from "antd";
import { CSSProperties, FC } from "react";
import { TWorkerNode } from "./types";

const defaultStyles: CSSProperties = {
  width: 80,
  height: 80,
  boxSizing: "border-box",
};

const selectedStyles: CSSProperties = {
  border: "2px solid blue",
};

const WorkerNode: FC<NodeProps<TWorkerNode>> = (props) => {
  return (
    <>
      <Card
        style={
          props.selected
            ? { ...defaultStyles, ...selectedStyles }
            : defaultStyles
        }
      >
        {props.id}
      </Card>
      <Handle type="source" position={Position.Left} />
      <Handle type="target" position={Position.Right} />
    </>
  );
};

export default WorkerNode;
