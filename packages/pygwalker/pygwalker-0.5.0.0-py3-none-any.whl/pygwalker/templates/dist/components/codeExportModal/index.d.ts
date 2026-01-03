import React from "react";
import type { VizSpecStore } from "@kanaries/graphic-walker/store/visualSpecStore";
interface ICodeExport {
    globalStore: React.MutableRefObject<VizSpecStore | null>;
    sourceCode: string;
    open: boolean;
    setOpen: (open: boolean) => void;
}
declare const CodeExport: React.FC<ICodeExport>;
export default CodeExport;
