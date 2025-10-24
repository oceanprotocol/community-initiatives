const axios = require("axios");
const sharp = require("sharp");
const fs = require("fs");
const path = require("path");

const imageUrl =
  "https://raw.githubusercontent.com/mikolalysenko/lena/master/lena.png";

async function applyFilters(imageUrl, filter) {
  if (!filter) {
    console.log("Filter is not provided.");
    return;
  }

  const response = await axios.get(imageUrl, { responseType: "arraybuffer" });
  const imageBuffer = Buffer.from(response.data);

  let processedImage;

  switch (filter) {
    case "blur":
      processedImage = await sharp(imageBuffer).blur(5).toBuffer();
      break;
    case "grayscale":
      processedImage = await sharp(imageBuffer).grayscale().toBuffer();
      break;
    case "unsharp":
      processedImage = await sharp(imageBuffer).sharpen(5, 1, 1).toBuffer();
      break;
    default:
      console.log("Unknown filter.");
      return;
  }

  return processedImage;
}

async function main() {
  const filteredImage = await applyFilters(imageUrl, "grayscale");

  const outputDir = "data/outputs";
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const outputPath = path.join(outputDir, "filtered_image.png");
  await fs.promises.writeFile(outputPath, filteredImage);

  console.log(`Filters applied and image saved successfully as ${outputPath}`);
}

main();
