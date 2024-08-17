export interface SplitPdfRequest {
  file: string;
  pages: number;
}

export interface MergePdfRequest {
  files: string[];
}

export interface EncryptPdfRequest {
  file: string;
  password: string;
}

export interface PdfToImagesRequest {
  file: string;
  format?: string;
  pages_per_image?: number;
  dpi?: number;
}

export interface RotatePdfRequest {
  file: string;
  angle: number;
}

export interface AddWaterMarkToPdfRequest {
  file: string;
  watermark_text: string;
  density: string;
}

export interface CompressPdfRequest {
  file: string;
  compression_level?: number;
}
