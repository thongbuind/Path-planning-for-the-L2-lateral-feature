const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { execFileSync } = require("node:child_process");

const site = __dirname;
const docs = path.join(site, "..", "docs");
const benchmark = JSON.parse(execFileSync("python3", [path.join(site, "latest_benchmark.py")], { encoding: "utf8" }));
const studyFigure = "research/studies/PP-TS-013-comfort-line/sample-r171-sbend.png";
const output = path.join(site, "dist");
const data = { window: {} };
vm.runInNewContext(fs.readFileSync(path.join(site, "cards.js"), "utf8"), data);
const reports = data.window.SPEC_CARDS.filter(card => card.kind === "doc");
const repository = (process.env.SPEC_WEB_GITHUB_REPOSITORY || "").trim();
if (repository && !/^[a-z\d][a-z\d-]{0,38}\/(?!\.{1,2}$)[a-z\d_.-]{1,100}$/i.test(repository)) {
  throw new Error("SPEC_WEB_GITHUB_REPOSITORY cần có dạng owner/repo");
}

const staging = fs.mkdtempSync(path.join(site, ".dist-"));
try {
  fs.mkdirSync(path.join(staging, "en"));
  fs.mkdirSync(path.join(staging, "vi"));
  for (const file of ["app.js", "cards.js", "docmd.js", "diagrams.js", "style.css", "reviews.js", "reviews.css", "en/strings.js"]) {
    fs.copyFileSync(path.join(site, file), path.join(staging, file));
  }
  // Bản tĩnh thay Workbench bằng trang hướng dẫn vì Workbench cần server cục bộ.
  fs.cpSync(path.join(site, "simulation-static"), path.join(staging, "simulation"), { recursive: true });
  fs.copyFileSync(path.join(docs, "en", "versions.json"), path.join(staging, "en", "versions.json"));
  for (const file of ["index.html", "report.html", "home/index.html", "technical-documents/index.html", "benchmark/index.html", "path-planner/index.html"]) {
    const html = fs.readFileSync(path.join(site, file), "utf8")
      .replace("<html ", "<html data-static ")
      .replace('<meta name="github-repository" content="">', '<meta name="github-repository" content="' + repository + '">');
    const destination = path.join(staging, file);
    fs.mkdirSync(path.dirname(destination), { recursive: true });
    fs.writeFileSync(destination, html);
  }
  const benchmarkOutput = path.join(staging, "benchmark", "run");
  fs.mkdirSync(benchmarkOutput);
  const hasEnglish = ["report-en.html", "report-en-details.html"].every(file => fs.existsSync(path.join(benchmark.run, file)));
  for (const file of ["report.html", "report-details.html", "report-en.html", "report-en-details.html", "results.jsonl", "generation.json", "conformance.json"]) {
    const sourceFile = !hasEnglish && file.startsWith("report-en") ? file.replace("-en", "") : file;
    fs.copyFileSync(path.join(file.startsWith("report") ? benchmark.run : benchmark.data, sourceFile), path.join(benchmarkOutput, file));
  }
  fs.mkdirSync(path.join(benchmarkOutput, "suite"));
  for (const file of ["results.jsonl", "generation.json", "conformance.json"]) {
    fs.copyFileSync(path.join(benchmark.data, file), path.join(benchmarkOutput, "suite", file));
  }
  const figureOutput = path.join(staging, studyFigure);
  fs.mkdirSync(path.dirname(figureOutput), { recursive: true });
  fs.copyFileSync(path.join(site, "..", studyFigure), figureOutput);
  for (const { doc } of reports) {
    if (!/^[a-z0-9][a-z0-9-]{0,63}$/.test(doc)) throw new Error("ID báo cáo không hợp lệ: " + doc);
    const file = doc + ".md";
    fs.copyFileSync(path.join(docs, "vi", file), path.join(staging, "vi", file));
    const translation = path.join(docs, "en", file);
    if (fs.existsSync(translation)) fs.copyFileSync(translation, path.join(staging, "en", file));
  }
  fs.writeFileSync(path.join(staging, ".nojekyll"), "");
  fs.rmSync(output, { recursive: true, force: true });
  fs.renameSync(staging, output);
} finally {
  fs.rmSync(staging, { recursive: true, force: true });
}

console.log("Bản tĩnh: " + output);
