import axios from "axios";
// import { getAuthToken } from "storage";

export const httpSignal = axios.CancelToken.source();

const logOutUser = () => {
  return (window.location.href = "");
};

const CancelToken = axios.CancelToken;
let requestSignal;

const config = {
  apiGateway: {
    BASE_URL: process.env.REACT_APP_DEV_API_BASE_URL,
  },
};

const { BASE_URL } = config.apiGateway;

const API = axios.create({
  baseURL: BASE_URL,
});

API.interceptors.request.use(
  (config) => {
    const accessToken = ""
    // const accessToken = getAuthToken();
    accessToken && (config.headers!.Authorization = "Bearer " + accessToken);
    requestSignal = CancelToken.source();
    config.cancelToken = requestSignal.token;
    return config;
  },
  (error) => {
    Promise.reject(error);
  }
);

API.interceptors.response.use(
  async (response) => {
    return response;
  },
  async (error) => {
    const status = error?.response?.status;
    if (status === 401) {
      sessionStorage.clear();
      logOutUser();
      return Promise.reject(error);
    }

    return Promise.reject(error);
  }
);

export default API;