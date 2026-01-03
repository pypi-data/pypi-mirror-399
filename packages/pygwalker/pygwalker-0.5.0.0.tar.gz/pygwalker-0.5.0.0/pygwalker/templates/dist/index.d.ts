import { IAppProps } from './interfaces';
import type { IPreviewProps, IChartPreviewProps } from './components/preview';
declare function GWalker(props: IAppProps, id: string): void;
declare function PreviewApp(props: IPreviewProps, containerId: string): void;
declare function ChartPreviewApp(props: IChartPreviewProps, id: string): void;
declare const _default: {
    GWalker: typeof GWalker;
    PreviewApp: typeof PreviewApp;
    ChartPreviewApp: typeof ChartPreviewApp;
    StreamlitGWalker: () => void;
    render: import("@anywidget/types").Render<{
        [x: string]: any;
    }>;
};
export default _default;
