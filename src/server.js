const fs = require("fs");
const fsp = require("fs/promises");
const http = require("http");
const os = require("os");
const path = require("path");
const { randomUUID } = require("crypto");
const { resolveConverter } = require("./converters");
const { convertWithFfmpeg } = require("./ffmpeg");

const PUBLIC_DIR = path.join(__dirname, "..", "public");
const MAX_UPLOAD_BYTES = 512 * 1024 * 1024;

function getContentType(filePath) {
  const extension = path.extname(filePath).toLowerCase();

  if (extension === ".html") {
    return "text/html; charset=utf-8";
  }

  if (extension === ".css") {
    return "text/css; charset=utf-8";
  }

  if (extension === ".js") {
    return "application/javascript; charset=utf-8";
  }

  return "application/octet-stream";
}

function sendJson(response, statusCode, payload) {
  const body = JSON.stringify(payload);
  response.writeHead(statusCode, {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(body)
  });
  response.end(body);
}

async function serveStaticFile(response, requestPath) {
  const normalizedPath = requestPath === "/" ? "/index.html" : requestPath;
  const safePath = path
    .normalize(normalizedPath)
    .replace(/^[/\\]+/, "")
    .replace(/^(\.\.[/\\])+/, "");
  const filePath = path.join(PUBLIC_DIR, safePath);

  if (!filePath.startsWith(PUBLIC_DIR)) {
    sendJson(response, 403, { error: "Forbidden" });
    return;
  }

  try {
    const stats = await fsp.stat(filePath);
    if (!stats.isFile()) {
      sendJson(response, 404, { error: "Not found" });
      return;
    }

    response.writeHead(200, {
      "Content-Type": getContentType(filePath),
      "Content-Length": stats.size
    });

    fs.createReadStream(filePath).pipe(response);
  } catch (error) {
    sendJson(response, 404, { error: "Not found" });
  }
}

function streamRequestToFile(request, destinationPath) {
  return new Promise((resolve, reject) => {
    let receivedBytes = 0;
    const writeStream = fs.createWriteStream(destinationPath);

    function fail(error) {
      request.destroy();
      writeStream.destroy();
      reject(error);
    }

    request.on("data", (chunk) => {
      receivedBytes += chunk.length;
      if (receivedBytes > MAX_UPLOAD_BYTES) {
        fail(new Error("Uploaded file is too large."));
        return;
      }

      writeStream.write(chunk);
    });

    request.on("end", () => {
      writeStream.end(() => resolve());
    });

    request.on("error", fail);
    writeStream.on("error", fail);
  });
}

async function handleConversion(request, response) {
  if (request.method !== "POST") {
    sendJson(response, 405, { error: "Method not allowed" });
    return;
  }

  const conversionId = randomUUID();
  const workDir = await fsp.mkdtemp(path.join(os.tmpdir(), `toolconv-${conversionId}-`));
  const inputPath = path.join(workDir, "input.mp4");
  const outputPath = path.join(workDir, "output.wav");

  try {
    await streamRequestToFile(request, inputPath);

    const converter = resolveConverter(inputPath, outputPath);
    if (!converter) {
      throw new Error("Unsupported conversion.");
    }

    await convertWithFfmpeg(converter.buildArgs(inputPath, outputPath));

    const stats = await fsp.stat(outputPath);
    response.writeHead(200, {
      "Content-Type": "audio/wav",
      "Content-Length": stats.size,
      "Content-Disposition": "attachment; filename=\"converted.wav\""
    });

    let cleanedUp = false;
    async function cleanup() {
      if (cleanedUp) {
        return;
      }

      cleanedUp = true;
      await fsp.rm(workDir, { recursive: true, force: true });
    }

    const readStream = fs.createReadStream(outputPath);
    readStream.pipe(response);
    response.on("close", cleanup);
    readStream.on("error", cleanup);
  } catch (error) {
    await fsp.rm(workDir, { recursive: true, force: true });
    sendJson(response, 500, { error: error.message });
  }
}

async function startServer({ port }) {
  const server = http.createServer((request, response) => {
    const requestUrl = new URL(request.url, `http://${request.headers.host || "127.0.0.1"}`);

    if (requestUrl.pathname === "/api/convert/mp4-to-wav") {
      handleConversion(request, response).catch((error) => {
        sendJson(response, 500, { error: error.message });
      });
      return;
    }

    serveStaticFile(response, requestUrl.pathname).catch((error) => {
      sendJson(response, 500, { error: error.message });
    });
  });

  await new Promise((resolve, reject) => {
    server.on("error", reject);
    server.listen(port, "127.0.0.1", resolve);
  });

  console.log(`Borstbindare Wenman UI is running at http://127.0.0.1:${port}`);
  console.log("Open that address in your browser to use the offline converter.");
}

module.exports = {
  startServer
};
