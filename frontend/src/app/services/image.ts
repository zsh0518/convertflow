import { request } from "../utils/request";
import * as apis from "../constants/apis";
import {
  AddWaterMarkToImagesRequest,
  GenerateImageRequest,
  JoinImagesRequest,
  RemoveImageBackgroundRequest,
  UpscaleImageRequest,
} from "../types/apis/image";

export async function addWaterMarkToImages(data: AddWaterMarkToImagesRequest) {
  const res = await request<Blob>(apis.AddWaterMarkToImage, {
    method: "post",
    data,
    responseType: "blob",
  });
  return res.data;
}

export async function removeImageBackground(
  data: RemoveImageBackgroundRequest
) {
  const res = await request<Blob>(apis.RemoveImageBackground, {
    method: "post",
    data,
    responseType: "blob",
  });
  return res.data;
}

export async function joinImages(data: JoinImagesRequest) {
  const res = await request<Blob>(apis.JoinImages, {
    method: "post",
    data,
    responseType: "blob",
  });
  return res.data;
}

export async function upscaleImage(data: UpscaleImageRequest) {
  const res = await request<Blob>(apis.UpscaleImage, {
    method: "post",
    data,
    responseType: "blob",
  });
  return res.data;
}

export async function generateImage(data: GenerateImageRequest) {
  const res = await request<Blob>(apis.GenerateImage, {
    method: "post",
    data,
    responseType: "blob",
  });
  return res.data;
}
