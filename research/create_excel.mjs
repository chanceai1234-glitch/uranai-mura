/**
 * 01_uranai_list.md + 02_uranai_logic.md + 04_output_type.md → uranai_master.xlsx
 * Run: node research/create_excel.mjs
 * 04: node research/build_output_type.mjs
 */
import fs from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";
import ExcelJS from "exceljs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const BASE = __dirname;
const FILE_01 = join(BASE, "01_uranai_list.md");
const FILE_02 = join(BASE, "02_uranai_logic.md");
const FILE_04 = join(BASE, "04_output_type.md");
const OUT = join(BASE, "uranai_master.xlsx");

function parseTableRows(body) {
  const out = {};
  for (const line of body.split(/\r?\n/)) {
    const t = line.trim();
    if (!t.startsWith("|")) continue;
    const cells = t
      .replace(/^\|/, "")
      .replace(/\|$/, "")
      .split("|")
      .map((c) => c.trim());
    if (cells.length < 2) continue;
    const [key, val] = cells;
    if (key === "項目" || key === "------" || !key) continue;
    out[key] = val;
  }
  return out;
}

function parse01(text) {
  const chunks = text.split(/\r?\n##### /).slice(1);
  return chunks.map((ch) => {
    const nl = ch.indexOf("\n");
    const body = nl === -1 ? "" : ch.slice(nl + 1);
    return parseTableRows(body);
  });
}

function parse02(text) {
  const chunks = text.split(/\r?\n### /).slice(1);
  return chunks.map((ch) => {
    const nl = ch.indexOf("\n");
    const body = nl === -1 ? "" : ch.slice(nl + 1);
    return parseTableRows(body);
  });
}

/** @returns {Record<string, { typ: string, det: string }>} */
function parse04(text) {
  const norm = text.replace(/\r\n/g, "\n");
  const map = {};
  for (const line of norm.split("\n")) {
    const t = line.trim();
    if (!t.startsWith("|")) continue;
    if (t.includes("占い名") && t.includes("出力方式")) continue;
    if (/^\|\s*[-:|]+\s*\|/.test(t)) continue;
    const cells = t
      .replace(/^\|/, "")
      .replace(/\|$/, "")
      .split("|")
      .map((c) => c.trim());
    if (cells.length < 2) continue;
    const [name, typ, det = ""] = cells;
    if (!name) continue;
    map[name] = { typ, det };
  }
  return map;
}

function colWidthUnits(str, maxW = 50) {
  if (!str) return 8;
  let w = 0;
  for (const ch of String(str)) {
    w += ch.codePointAt(0) < 128 ? 1 : 2;
  }
  return Math.min(Math.max(w * 0.55 + 2, 8), maxW);
}

const headers = [
  "No.",
  "占い名",
  "発祥地・文化圏",
  "カテゴリ",
  "必要な入力情報",
  "判定ロジック概要",
  "出力内容",
  "更新頻度",
  "実装難易度",
  "出力方式",
  "出力方式詳細",
  "実装メモ",
  "概要メモ",
];

const t1 = fs.readFileSync(FILE_01, "utf8");
const t2 = fs.readFileSync(FILE_02, "utf8");
const t4 = fs.readFileSync(FILE_04, "utf8");
const list01 = parse01(t1);
const list02 = parse02(t2);
const outType = parse04(t4);

if (list01.length !== list02.length) {
  console.error(`件数不一致: 01=${list01.length} 02=${list02.length}`);
  process.exit(1);
}

const wb = new ExcelJS.Workbook();
const ws = wb.addWorksheet("占い一覧", {
  views: [{ state: "frozen", ySplit: 1 }],
});

ws.addRow(headers);
const headerRow = ws.getRow(1);
headerRow.font = { name: "Meiryo UI", size: 11, bold: true };
headerRow.alignment = { vertical: "middle", horizontal: "center", wrapText: true };
headerRow.fill = {
  type: "pattern",
  pattern: "solid",
  fgColor: { argb: "FFCCCCCC" },
};
headerRow.height = 22;

const colMax = headers.map(() => 8);

for (let i = 0; i < headers.length; i++) {
  colMax[i] = Math.max(colMax[i], colWidthUnits(headers[i]));
}

for (let i = 0; i < list01.length; i++) {
  const d1 = list01[i];
  const d2 = list02[i];
  const r = i + 2;
  const name = d2["占い名"] || d1["占い名"] || "";
  const ot = outType[name] || { typ: "", det: "" };
  if (name && !outType[name]) {
    console.warn(`警告: 04_output_type.md に占い名がありません: ${JSON.stringify(name)}`);
  }
  const vals = [
    i + 1,
    name,
    d1["発祥地・文化圏"] || "",
    d1["出力カテゴリ"] || "",
    d2["必要な入力情報"] || "",
    d2["判定ロジック概要"] || "",
    d2["出力内容"] || "",
    d2["更新頻度"] || "",
    d2["実装難易度"] || "",
    ot.typ,
    ot.typ === "C" ? ot.det : "",
    d2["実装メモ"] || "",
    d1["概要メモ"] || "",
  ];
  ws.addRow(vals);
  const row = ws.getRow(r);
  row.font = { name: "Meiryo UI", size: 11 };
  row.alignment = { vertical: "top", wrapText: true };
  if (r % 2 === 0) {
    row.fill = {
      type: "pattern",
      pattern: "solid",
      fgColor: { argb: "FFF5F5F5" },
    };
  }
  vals.forEach((v, c) => {
    colMax[c] = Math.max(colMax[c], colWidthUnits(v));
  });
}

ws.columns = headers.map((_, i) => ({
  width: Math.min(colMax[i], 50),
}));

await wb.xlsx.writeFile(OUT);
console.log(`Wrote ${OUT} (${list01.length} data rows)`);
