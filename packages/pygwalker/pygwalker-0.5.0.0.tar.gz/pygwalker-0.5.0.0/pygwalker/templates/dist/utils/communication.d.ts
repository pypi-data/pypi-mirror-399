interface IResponse {
    data?: any;
    message?: string;
    code: number;
}
interface ICommunication {
    sendMsg: (action: string, data: any, timeout?: number) => Promise<IResponse>;
    registerEndpoint: (action: string, callback: (data: any) => any) => void;
    sendMsgAsync: (action: string, data: any, rid: string | null) => void;
}
declare const initJupyterCommunication: (gid: string) => {
    sendMsg: (action: string, data: any, timeout?: number) => Promise<any>;
    registerEndpoint: (action: string, callback: (data: any) => any) => void;
    sendMsgAsync: (action: string, data: any, rid: string | null) => void;
};
declare const initHttpCommunication: (gid: string, baseUrl: string) => Promise<{
    sendMsg: (action: string, data: any, timeout?: number) => Promise<any>;
    registerEndpoint: (_: string, __: (data: any) => any) => void;
    sendMsgAsync: (action: string, data: any) => Promise<any>;
}>;
declare const streamlitComponentCallback: (data: any) => void;
declare const initAnywidgetCommunication: (gid: string, model: import("@anywidget/types").AnyModel) => Promise<{
    sendMsg: (action: string, data: any, timeout?: number) => Promise<any>;
    registerEndpoint: (_: string, __: (data: any) => any) => void;
    sendMsgAsync: (action: string, data: any, rid: string | null) => void;
}>;
export type { ICommunication };
export { initJupyterCommunication, initHttpCommunication, streamlitComponentCallback, initAnywidgetCommunication };
