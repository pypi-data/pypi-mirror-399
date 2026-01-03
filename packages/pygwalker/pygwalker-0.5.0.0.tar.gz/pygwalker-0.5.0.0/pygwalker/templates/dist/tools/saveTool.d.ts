import React from 'react';
import type { IAppProps } from '../interfaces';
import type { IGWHandler } from '@kanaries/graphic-walker/interfaces';
import type { ToolbarButtonItem } from "@kanaries/graphic-walker/components/toolbar/toolbar-button";
import type { VizSpecStore } from '@kanaries/graphic-walker/store/visualSpecStore';
export declare function getSaveTool(props: IAppProps, gwRef: React.MutableRefObject<IGWHandler | null>, storeRef: React.MutableRefObject<VizSpecStore | null>, isChanged: boolean, setIsChanged: React.Dispatch<React.SetStateAction<boolean>>): ToolbarButtonItem;
