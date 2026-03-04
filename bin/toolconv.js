#!/usr/bin/env node

const { runCli } = require("../src/cli");

runCli(process.argv.slice(2))
  .then((exitCode) => {
    process.exitCode = exitCode;
  })
  .catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
  });
