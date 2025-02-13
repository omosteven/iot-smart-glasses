import { ReactNode } from "react";
import { toast } from "react-toastify";

const toastMessage = (content: ReactNode, hasError?: Boolean) => {
  return hasError ? toast.error(content) : toast(content);
};

export default toastMessage;
