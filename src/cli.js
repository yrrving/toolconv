const fs = require("fs");
const path = require("path");
const { resolveConverter, listSupportedConversions } = require("./converters");
const { ensureFfmpegAvailable, convertWithFfmpeg } = require("./ffmpeg");

function helpText() {
  const conversions = listSupportedConversions()
    .map(({ from, to, description }) => `  ${from} -> ${to}  ${description}`)
    .join("\n");

  return [
    "Borstbindare Wenman",
    "Offline media conversion CLI",
    "",
    "Usage:",
    "  toolconv convert <input-file> <output-file>",
    "  borstbindare-wenman convert <input-file> <output-file>",
    "",
    "Supported conversions:",
    conversions,
    "",
    "Examples:",
    "  toolconv convert clip.mp4 clip.wav",
    "  borstbindare-wenman convert /path/in.mp4 /path/out.wav"
  ].join("\n");
}

function validatePaths(inputPath, outputPath) {
  if (!fs.existsSync(inputPath)) {
    throw new Error(`Input file does not exist: ${inputPath}`);
  }

  const absoluteInput = path.resolve(inputPath);
  const absoluteOutput = path.resolve(outputPath);

  if (absoluteInput === absoluteOutput) {
    throw new Error("Input and output paths must be different.");
  }

  const outputDir = path.dirname(absoluteOutput);
  if (!fs.existsSync(outputDir)) {
    throw new Error(`Output directory does not exist: ${outputDir}`);
  }
}

async function runConvert(args) {
  if (args.length !== 2) {
    throw new Error("convert requires exactly two arguments: <input-file> <output-file>");
  }

  const [inputPath, outputPath] = args;
  validatePaths(inputPath, outputPath);

  const converter = resolveConverter(inputPath, outputPath);
  if (!converter) {
    const supported = listSupportedConversions()
      .map(({ from, to }) => `${from} -> ${to}`)
      .join(", ");

    throw new Error(
      `Unsupported conversion for ${path.extname(inputPath) || "unknown"} -> ${path.extname(outputPath) || "unknown"}. Supported conversions: ${supported}`
    );
  }

  await ensureFfmpegAvailable();
  await convertWithFfmpeg(converter.buildArgs(inputPath, outputPath));
  console.log(`Created ${path.resolve(outputPath)}`);
  return 0;
}

async function runCli(args) {
  if (args.length === 0 || args[0] === "help" || args[0] === "--help" || args[0] === "-h") {
    console.log(helpText());
    return 0;
  }

  const [command, ...commandArgs] = args;
  if (command === "convert") {
    return runConvert(commandArgs);
  }

  throw new Error(`Unknown command: ${command}\n\n${helpText()}`);
}

module.exports = {
  helpText,
  runCli
};
