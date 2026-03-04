const path = require("path");

function normalizeExtension(value) {
  return value.replace(/^\./, "").toLowerCase();
}

function getExtension(filePath) {
  return normalizeExtension(path.extname(filePath));
}

const converters = {
  "mp4:wav": {
    description: "Extract audio from MP4 video and write it as WAV.",
    buildArgs(inputPath, outputPath) {
      return [
        "-y",
        "-i",
        inputPath,
        "-vn",
        "-acodec",
        "pcm_s16le",
        outputPath
      ];
    }
  }
};

function resolveConverter(inputPath, outputPath) {
  const key = `${getExtension(inputPath)}:${getExtension(outputPath)}`;
  return converters[key] || null;
}

function listSupportedConversions() {
  return Object.entries(converters).map(([key, converter]) => {
    const [from, to] = key.split(":");
    return {
      from,
      to,
      description: converter.description
    };
  });
}

module.exports = {
  getExtension,
  listSupportedConversions,
  resolveConverter
};
