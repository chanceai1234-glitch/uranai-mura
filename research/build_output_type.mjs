/**
 * 01 + 02 を読み、224件の出力方式(A/B/C)を判定して 04_output_type.md を生成する。
 * node research/build_output_type.mjs
 */
import fs from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const BASE = __dirname;

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
  const chunks = text.replace(/\r\n/g, "\n").split("\n##### ").slice(1);
  return chunks.map((ch) => {
    const nl = ch.indexOf("\n");
    const body = nl === -1 ? "" : ch.slice(nl + 1);
    return parseTableRows(body);
  });
}

function parse02(text) {
  const chunks = text.replace(/\r\n/g, "\n").split("\n### ").slice(1);
  return chunks.map((ch) => {
    const nl = ch.indexOf("\n");
    const body = nl === -1 ? "" : ch.slice(nl + 1);
    return parseTableRows(body);
  });
}

/** @returns {[string, string]} [A|B|C, detail≤50 for C only] */
function classify(name, d1, d2) {
  const logic = d2["判定ロジック概要"] || "";
  const memo = d1["概要メモ"] || "";
  const input = d2["必要な入力情報"] || "";
  const blob = `${name}\n${logic}\n${memo}\n${input}`;

  // --- C: 媒体・総称・文献分類など（占術アルゴリズムが一義でない）---
  const cRules = [
    [/リモート占いサービス/, "配信形態のみで占術本体は占師・方式依存"],
    [/メール占い・電話占い/, "商流形態であり方式は占師任せ"],
    [/民族口承占い|口述資料ベース/, "民族誌再構成で統一断法がない"],
    [/ジャワン占い（総称）/, "総称で内部方式が多様"],
    [/マレー伝統占（複合）/, "複合民俗で単一ルールに収まらない"],
    [/オーストラリア先住民占断（総称）/, "地域・口承差が大きく総称"],
    [/伝統治療者占い/, "医療文化実践で占断様式が多様"],
    [/スワヒリ海岸占い/, "地域口承の総称で方式固定困難"],
    [/中央アジア民間占星・夢占/, "占星と夢の民俗が混在する総称"],
    [/コーカサス教会暦・民間兆候/, "教会暦と兆候信仰の複合"],
    [/砂漠民間占/, "遊牧民間信仰の総称"],
    [/北欧金属・石占い（民俗）/, "民俗実践で型が文献化しにくい"],
    [/ウィスパリング・シェル/, "民族誌記載ベースで再現手順が曖昧"],
    [/民族誌記載系/, "記載ベースで再現手順が曖昧"],
    [/文献分類/, "学術分類であり自動占断手順ではない"],
    [/歴史）$|（歴史）/, "歴史記述が主で現代占断手順ではない"],
    [/死霊占い（文献分類）/, "文献ジャンル分類"],
    [/頭蓋骨占い（歴史）/, "歴史占術の記述"],
    [/イスラム圏内の占星慣行/, "地域慣行の総称"],
    [/僧伽罗・ネパール系占星/, "地域占星の総称"],
    [/大洋州島嶼部口述占い/, "島嶼口述の総称"],
    [/フィジー・タヒチ占い/, "ポリネシア地域差が大きい"],
    [/性格タイプ診断（占い包装）/, "心理検査包装で占術本体は別扱いが妥当"],
    [/ロマ占い（カード・手相）/, "商業ステレオタイプで実体が一定しない"],
    [/ロマ（ジプシー）占い/, "商業演出中心で方式が固定されにくい"],
    [/物体霊読（自称）/, "主観的主張ベースで検証困難"],
    [/チャネリング系（英語圏）/, "スピ系総称で手順が多様"],
    [/水晶占い（スクリュー／ジプシー系演出）/, "演出中心で客観ルールが弱い"],
    [/水晶玉占い（クリスタロマンシー）/, "玉視は解釈が鑑定者依存"],
    [/水晶占い$/, "水晶視は解釈が鑑定者依存"], // 欧州の水晶占い（重複名注意: 421行は上で、1573は別）
  ];
  for (const [re, detail] of cRules) {
    if (re.test(name)) return ["C", detail.slice(0, 50)];
  }

  // --- B: 人の直感・解釈・霊的実践・パターン読み ---
  const bBlob = blob;
  if (
    /チャネリング|守護霊メッセージ|守護天使|霊視|ムードン|巫俗|巫堂|シャーマン|ボー（シャーマン）|テングリ|サンゴマ|ナキンガス|イファ|オペレ|ディレ・カウリ|ウンバンダ|カンドンブレ|ヴードゥー|幻視|アヤワスカ|ビジョン|スピリット|トーテム|スマッジ|癒し儀礼|夢の時代|トゥクラ|神託|デルポイ|扶鸞|扶乩|鸞占|神判|湯占|サイコメトリー|物体霊/.test(
      bBlob
    )
  ) {
    return ["B", ""];
  }
  if (
    /手相|人相|面相|骨相|体相|摸骨|サムドリカ|パンガラオ|インド手相|西洋手相|ハスタ|筆跡|グラフォ|茶葉|紅茶占い|コーヒー残渣|コーヒー占い|タッセオ|溶鉛|ろうそく・溶鉛|蝋の形|クラロスクピー|溶蝋|りんご皮|雲占い|炎・灰|香煙|バルト金属|音感|色占い|クロノマンシー|臓器占い|鳥占い（古代|鳥占（オスカ|動物の偶然|アパントマンシー|ケファロマンシー|頭蓋骨|ネクロマンシー|夢占い|夢の内容|心理折衷|砂占い（サヘル）|骨・氷・光|イヌイット骨|メラネシア骨|羊骨|羊肩甲骨|カウリ|貝占|贝壳|棋占い|象棋占|圍棋占|遊戯占|測字|そくじ|ダウジング|振り子|ペンデュラム|オーラ|波動・オーラ|ルーン|符文|オーガム|ケルト十字|タロット|ルノルマン|オラクルカード|オラクルデッキ|キッパー|プレイングカード|トランプ占い|カルトマンシー|御神籤.*対面|おみくじ.*人|巫堂|グッ|굿/.test(
      name
    )
  ) {
    // デジタル自動系は後段でAに上書きしない — 名前で除外
    if (
      /デジタル|自動引き|API|アプリ|Web|スプレッドシート|電子|公式デジタル|SNS星座|ホロスコープ（短文）|生成AI|ボット|LLM|亀甲占い（商代|卜）/.test(
        name
      )
    ) {
      /* fall through to A checks */
    } else if (/タロット|ルノルマン|オラクル|キッパー|トランプ|ケルト十字/.test(name)) {
      return ["B", ""];
    } else if (/御神籤|おみくじ|求籤|籤|擲筊|擲杯|杯珓|杯教|デジタル御神籤|電子おみくじ|公式デジタル籤|オンチェーン/.test(name)) {
      /* おみくじ類は主にA */
    } else {
      return ["B", ""];
    }
  }

  // タロット・ルノルマン等（名称に明示で未処理）
  if (
    /タロット|ルノルマン（仏）|ルノルマンカード|オラクルカード|キッパーカード|プレイングカード|トランプ占い|ケルト十字/.test(
      name
    ) &&
    !/デジタル|自動|API|アプリ/.test(name)
  ) {
    return ["B", ""];
  }

  // 夢占い（文献系除く）
  if (/夢占い|夢の時代|エジプト夢占/.test(name)) {
    if (/文献|蔵書/.test(name)) return ["C", "古代文献の夢占資料で現代手順は別"];
    return ["B", ""];
  }

  // 易・卦：操作は乱数化可能 → A
  // 四柱・占星・数秘・暦 → A
  // おみくじ・籤・サイコロ・コイン → A

  // 明示B: シャーマン・アンデス等（名称）
  if (
    /占断$|シャーマン|マチ占|クルカンドゥ|マポチェ|サンテリア|ルクミ|ハイチ|パシュトゥーン口述|モ占い$|チベット・モ（骰子）|骰子占い|モ（骰子）占い/.test(
      name
    ) &&
    !/タイ占星|計算/.test(logic)
  ) {
    if (/タイ占星術|ビルマ|クメール|干支年運/.test(name)) return ["A", ""];
    if (/口述|占断（総称）|先住民/.test(name)) return ["B", ""];
  }

  if (/ボー（シャーマン）|巫堂占い|巫俗（ムードン）|サンゴマ|ナキンガス|砂占い（サヘル）|アンデス・クルカンドゥ|アヤワスカ|マチ占断|ディラゴゴ|ウンバンダ|カンドンブレ|ヴードゥー占断/.test(name))
    return ["B", ""];

  if (/イファ|カウリ貝占い|ディレ・カウリ/.test(name)) return ["B", ""];

  // デジタル・API・自動盤 → A
  if (
    /デジタル|自動|API|アプリ|Web／|スプレッドシート|電子おみくじ|公式デジタル|生成AI|LLM|チャットボット|対話型占いボット|ボット占い|SNS|ホロスコープ|占星API|オンチェーン|ゲーム内占い|VTuber|バーチャル|マッチングアプリ|亀甲占い（商代|自動命盤|易占いアプリ|紫微斗数Web|電子/.test(
      name
    )
  ) {
    return ["A", ""];
  }

  // 02で明示：主観再現が困難＝鑑定者依存（機械的再現ではない）
  if (/主観再現困難/.test(logic)) return ["B", ""];

  // Default A: 計算・マスタ・ルールエンジンが02で想定される占術
  if (
    /算出|計算|アルゴリズム|ルール|テンプレ|辞書|辞典|テーブル|盤|排盤|起局|乱数|マスタ|コード化|スコア|構造化/.test(
      logic
    )
  ) {
    return ["A", ""];
  }

  // 入力が主に日時・生年月日・方位図など構造化 → A 寄り
  if (
    /生年|生年月日|日時|質問.*日時|ホロスコープ|暦|干支|星座|八字|四柱|紫微|奇門|六壬|梅花|六爻|姓名|画数|数秘|血液型|動物占い|誕生花|家相|風水|ヴァーストゥ|ジェマトリア|カバラ|イスラム占星|ヒューマンデザイン|遺伝子占い|DNA|マヤ暦|トナルポウアリ|十三の月|ドリームスペル|ヒジュラ|吉日|ムフルタ|プラシュナ|ホラリー|合婚|秤骨|生肖|太歳|納音|七政|二十八宿|鉄板神数|河洛理数|皇極|文王卦|擇日|通勝|六曜|太乙|演禽|宿曜|密教系星占|陰陽道|算木|籤引き|吉祥番号|プリンボン|パウコン|ヴェーダ|ジョーティシャ|KPシステム|ナーディ|ラーマル|ラムル|イルム|クルアーン開き|ペルシャ|ゾロアスター|ヘレニズム|ギリシャ・ローマ|デカン|メディスン・ホイール（構造化）|トーテム/.test(
      blob
    )
  ) {
    // トーテムはスピ系でBにした — 再チェック
    if (/トーテム|スピリットアニマル/.test(name)) return ["B", ""];
    if (/メディスン・ホイール/.test(name)) return ["B", ""];
    return ["A", ""];
  }

  return ["C", "方式が文献・民俗に分散し機械化可否が一義でない"];
}

function main() {
  const t1 = fs.readFileSync(join(BASE, "01_uranai_list.md"), "utf8");
  const t2 = fs.readFileSync(join(BASE, "02_uranai_logic.md"), "utf8");
  const list01 = parse01(t1);
  const list02 = parse02(t2);
  if (list01.length !== list02.length) {
    console.error(`件数不一致: 01=${list01.length} 02=${list02.length}`);
    process.exit(1);
  }

  const rows = [];
  let a = 0,
    b = 0,
    c = 0;
  for (let i = 0; i < list01.length; i++) {
    const d1 = list01[i];
    const d2 = list02[i];
    const name = d2["占い名"] || d1["占い名"] || "";
    let [typ, det] = classify(name, d1, d2);
    if (typ === "A") a++;
    else if (typ === "B") b++;
    else c++;
    rows.push({ name, typ, det });
  }

  const lines = [
    "# 占い村リサーチ：出力方式（224件）",
    "",
    "`01_uranai_list.md` と `02_uranai_logic.md` を踏まえ、機械出力可否の観点で A/B/C 区分した。",
    "",
    "| 占い名 | 出力方式 | 詳細（Cの場合のみ） |",
    "|--------|----------|----------------------|",
  ];
  for (const r of rows) {
    const det = r.typ === "C" ? r.det.replace(/\|/g, "｜") : "";
    lines.push(`| ${r.name.replace(/\|/g, "｜")} | ${r.typ} | ${det} |`);
  }
  lines.push("");
  lines.push(`**集計:** A=${a}件 / B=${b}件 / C=${c}件 / 合計=${a + b + c}件`);
  lines.push("");
  lines.push(`<!-- 集計: A=${a} / B=${b} / C=${c} / 計=${a + b + c} -->`);

  fs.writeFileSync(join(BASE, "04_output_type.md"), lines.join("\n"), "utf8");
  console.log(`Wrote 04_output_type.md  A=${a} B=${b} C=${c} total=${a + b + c}`);
}

main();
