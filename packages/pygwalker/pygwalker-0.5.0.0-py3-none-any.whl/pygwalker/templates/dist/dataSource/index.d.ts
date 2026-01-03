import type { IDataSourceProps } from "../interfaces";
import type { IRow, IDataQueryPayload } from "@kanaries/graphic-walker/interfaces";
interface ICommPostDataMessage {
    dataSourceId: string;
    data?: IRow[];
    total: number;
    curIndex: number;
}
export declare function loadDataSource(props: IDataSourceProps): Promise<IRow[]>;
export declare function postDataService(msg: ICommPostDataMessage): void;
export declare function finishDataService(msg: any): void;
export declare function getDatasFromKernelBySql(fieldMetas: any): (payload: IDataQueryPayload) => Promise<IRow[]>;
export declare function getDatasFromKernelByPayload(payload: IDataQueryPayload): Promise<IRow[]>;
export {};
