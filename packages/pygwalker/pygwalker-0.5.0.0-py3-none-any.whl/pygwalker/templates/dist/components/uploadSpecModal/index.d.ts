import React from "react";
import type { VizSpecStore } from '@kanaries/graphic-walker/store/visualSpecStore';
interface IUploadSpecModal {
    setGwIsChanged: React.Dispatch<React.SetStateAction<boolean>>;
    storeRef: React.MutableRefObject<VizSpecStore | null>;
}
declare const UploadSpecModal: React.FC<IUploadSpecModal>;
export default UploadSpecModal;
