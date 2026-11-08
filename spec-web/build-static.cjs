// Xuất bản đọc tĩnh từ các báo cáo và bản dịch hiện có.
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const site = __dirname;
const docs = path.join(site, "..", "docs");
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
  fs.copyFileSync(path.join(docs, "en", "versions.json"), path.join(staging, "en", "versions.json"));
  for (const file of ["index.html", "report.html"]) {
    const html = fs.readFileSync(path.join(site, file), "utf8")
      .replace("<html ", "<html data-static ")
      .replace('<meta name="github-repository" content="">', '<meta name="github-repository" content="' + repository + '">');
    fs.writeFileSync(path.join(staging, file), html);
  }
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
