const test = require("node:test");
const assert = require("node:assert/strict");
const { helpText, runCli } = require("../src/cli");

test("help text includes branded name and supported conversion", () => {
  const text = helpText();

  assert.match(text, /Borstbindare Wenman/);
  assert.match(text, /mp4 -> wav/);
});

test("runCli returns zero for help", async () => {
  const exitCode = await runCli(["--help"]);
  assert.equal(exitCode, 0);
});

test("runCli rejects unknown command", async () => {
  await assert.rejects(
    () => runCli(["unknown-command"]),
    /Unknown command: unknown-command/
  );
});
