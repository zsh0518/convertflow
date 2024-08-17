import {
  AddWaterMarkToPdfRequest,
  CompressPdfRequest,
  EncryptPdfRequest,
  MergePdfRequest,
  PdfToImagesRequest,
  RotatePdfRequest,
  SplitPdfRequest,
} from "../types/apis/pdf";
import { request } from "../utils/request";
import * as apis from "../constants/apis";

export async function splitPdf(data: SplitPdfRequest) {
  const res = await request<Blob>(apis.SplitPdf, {
    method: "post",
    data,
    responseType: "blob",
  });
  return res.data;
}

export async function mergePdf(data: MergePdfRequest) {
  const res = await request<Blob>(apis.MergePdf, {
    method: "post",
    data,
    responseType: "blob",
  });
  return res.data;
}

export async function encryptPdf(data: EncryptPdfRequest) {
  const res = await request<Blob>(apis.EncryptPdf, {
    method: "post",
    data,
    responseType: "blob",
  });
  return res.data;
}

export async function pdfToImages(data: PdfToImagesRequest) {
  const res = await request<Blob>(apis.PdfToImages, {
    method: "post",
    data,
    responseType: "blob",
  });
  return res.data;
}

export async function rotatePdf(data: RotatePdfRequest) {
  const res = await request<Blob>(apis.RotatePdf, {
    method: "post",
    data,
    responseType: "blob",
  });
  return res.data;
}

export async function addWaterMarkToPdf(data: AddWaterMarkToPdfRequest) {
  const res = await request<Blob>(apis.AddWaterMarkToPdf, {
    method: "post",
    data,
    responseType: "blob",
  });
  return res.data;
}

export async function compressPdf(data: CompressPdfRequest) {
  const res = await request<Blob>(apis.CompressPdf, {
    method: "post",
    data,
    responseType: "blob",
  });
  return res.data;
}
