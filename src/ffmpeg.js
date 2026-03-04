const { spawn } = require("child_process");

function runProcess(command, args, stdio = "inherit") {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      stdio
    });

    child.on("error", (error) => {
      reject(error);
    });

    child.on("close", (code) => {
      if (code === 0) {
        resolve();
        return;
      }

      reject(new Error(`${command} exited with code ${code}.`));
    });
  });
}

async function ensureFfmpegAvailable() {
  try {
    await runProcess("ffmpeg", ["-version"], "ignore");
  } catch (error) {
    throw new Error(
      "ffmpeg is required but was not found in PATH. Install ffmpeg locally, then run the command again."
    );
  }
}

async function convertWithFfmpeg(args) {
  await runProcess("ffmpeg", args);
}

module.exports = {
  convertWithFfmpeg,
  ensureFfmpegAvailable
};
