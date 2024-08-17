export interface AddWaterMarkToImagesRequest {
  files: string[];
  watermark_text: string;
}

export interface RemoveImageBackgroundRequest {
  file: string;
}

export interface JoinImagesRequest {
  files: string;
  direction?: string;
}

export interface UpscaleImageRequest {
  file: string;
}

export interface GenerateImageRequest {
  prompt?: string;
  aspect_ratio?: string;
  num_outputs?: number;
  output_format?: string;
  output_quality?: number;
  disable_safety_checker?: boolean;
}
