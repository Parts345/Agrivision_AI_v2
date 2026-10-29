// Resize large phone photos in the browser before uploading. A 12 MP camera
// photo can be 4–6 MB; the model only needs a few hundred pixels.
const MAX_SIDE = 1280;
const JPEG_QUALITY = 0.88;

export async function prepareImage(file) {
  if (!file.type.startsWith("image/")) throw new Error("not-image");
  try {
    const bitmap = await createImageBitmap(file, { imageOrientation: "from-image" });
    const scale = Math.min(1, MAX_SIDE / Math.max(bitmap.width, bitmap.height));
    const width = Math.round(bitmap.width * scale);
    const height = Math.round(bitmap.height * scale);

    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    canvas.getContext("2d").drawImage(bitmap, 0, 0, width, height);
    bitmap.close?.();

    const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", JPEG_QUALITY));
    if (!blob) return file;
    return new File([blob], "leaf.jpg", { type: "image/jpeg" });
  } catch {
    // Browser cannot decode this format (e.g. some HEIC files): send the original.
    return file;
  }
}
