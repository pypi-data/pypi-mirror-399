import React from 'react';
import type { IAppProps } from '../interfaces';
import type { ToolbarButtonItem } from "@kanaries/graphic-walker/components/toolbar/toolbar-button";
import type { VizSpecStore } from '@kanaries/graphic-walker/store/visualSpecStore';
export declare function getExportDataframeTool(props: IAppProps, storeRef: React.MutableRefObject<VizSpecStore | null>): ToolbarButtonItem;
