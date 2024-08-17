import axios, { AxiosRequestConfig, AxiosResponse } from "axios";

export function request<T>(url: string, config?: Omit<AxiosRequestConfig, 'url'>) {
  return axios<T>({
    url,
    ...config,
  });
};
