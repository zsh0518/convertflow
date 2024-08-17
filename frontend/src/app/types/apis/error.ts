export interface ValidationError {
  detail?: {
    loc?: (number | string)[];
    msg?: string;
    type?: string;
  }[];
}
