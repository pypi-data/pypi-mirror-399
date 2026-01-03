import type { IChart } from "@kanaries/graphic-walker/interfaces";
export declare function usePythonCode(props: {
    sourceCode: string;
    visSpec: IChart[];
    version: string;
}): {
    pyCode: string;
};
