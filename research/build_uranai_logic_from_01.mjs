/**
 * Reads 01_uranai_list.md and writes 02_uranai_logic.md (implementation-oriented).
 * Run from repo root: node research/build_uranai_logic_from_01.mjs
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = __dirname;
const SRC = path.join(ROOT, "01_uranai_list.md");
const OUT = path.join(ROOT, "02_uranai_logic.md");

function parseEntries(text) {
  const parts = text.split(/\r?\n##### /);
  const entries = [];
  for (let i = 1; i < parts.length; i++) {
    const chunk = parts[i];
    const lines = chunk.split(/\r?\n/);
    const title = lines[0].trim();
    const body = lines.slice(1).join("\n");
    const row = {
      title,
      占い名: title,
      必要な入力情報: "",
      出力カテゴリ: "",
      更新頻度: "",
      実装難易度: "",
      概要メモ: "",
    };
    for (const key of Object.keys(row).filter((k) => k !== "title")) {
      const re = new RegExp(`\\|\\s*${key}\\s*\\|\\s*([^|]*?)\\s*\\|`);
      const m = body.match(re);
      if (m) row[key] = m[1].trim();
    }
    if (row["占い名"]) entries.push(row);
  }
  return entries;
}

function normalizeDifficulty(s) {
  s = (s || "").trim();
  if (s.includes("難")) return "難";
  if (s.includes("易") && !s.includes("中")) return "易";
  if (s.includes("中") || s.includes("易")) return "中";
  return "中";
}

function logicOutline(name, summary, inputs, outCat) {
  const n = name + (summary || "") + (inputs || "");
  if (/ランダム|抽|おみくじ|籤/.test(summary || "") || /おみくじ|籤詩/.test(n))
    return "暗号論的乱数で結果IDを選び、マスタのテキストを返す。";
  if (/四柱|八字|子平|Saju|사주/.test(n))
    return "節入り・TZを固定し生時から四柱を算出。十神・五行・大運・流年ルールをコード化して文案生成。";
  if (/紫微/.test(n))
    return "命盤起こしアルゴリズム（流派テーブル）→宮位・星曜→大限・流年で評価。";
  if (/奇門|六壬|太乙/.test(n))
    return "鑑定日時から式盤を計算し、門・星・神将等のテーブル演算で吉凶・方位を導出。";
  if (/六爻|文王卦|銭卦/.test(n))
    return "6爻生成（乱数）→本卦・変卦→納甲・世応等のルールで卦辞・爻辞を合成。";
  if (/梅花/.test(n))
    return "数・時刻等から卦を構成し体用生克で吉凶。辞書＋ルールエンジン。";
  if (/周易|蓍草|筮法/.test(n))
    return "筮操作をシミュレートまたは簡略化し卦を得て卦辞・爻辞を返す。";
  if (/姓名|画数/.test(n))
    return "正規化漢字→画数辞書→五格等の計算式→テンプレ文案。";
  if (/手相|ハスタ|パンガラオ/.test(n))
    return "画像MLまたはユーザー選択特徴→手相辞典から文案。";
  if (/人相|面相|サムドリカ/.test(n))
    return "顔ランドマーク／属性入力→相法テーブルで文案。";
  if (/骨相|摸骨/.test(n))
    return "身体データの代替入力＋文献ベース定性マスタ。";
  if (/体相/.test(n) && !/サムドリカ/.test(n))
    return "体型等の選択式入力→相法テーブル照合。";
  if (/擇日|暦注|通勝/.test(n))
    return "旧暦・神煞マスタで行事カテゴリ別に吉日スコア。";
  if (/六曜/.test(n))
    return "日付→旧暦→六曜計算式でラベル出力。";
  if (/宿曜|二十七宿/.test(n))
    return "誕生日等から本命宿・日宿を計算し吉凶マスタ参照。";
  if (/九星|気学/.test(n))
    return "本命星・鑑定年・方位から九星盤計算式で文案。";
  if (/西洋占星|ホロスコープ|ヘレニズム|ギリシャ・ローマ占星/.test(n))
    return "出生地・時刻から黄道座標・ハウス分割（エフェメリス）→アスペクト・トランジット。";
  if (/太陽星座|サンサイン|SNSホロスコープ/.test(n))
    return "月日→太陽星座→日付キーでCMSテンプレ運勢文。";
  if (/タロット|ルノルマン|オラクル|キッパー|ケルト十字/.test(n))
    return "シャッフル乱数→スプレッド位置にカード割当→意味テーブル合成。";
  if (/数秘/.test(n))
    return "生年月日・名前の数値還元→ライフパス等の固定式。";
  if (/血液型/.test(n))
    return "血液型キー→性格・相性マスタ。";
  if (/夢占い|夢の象徴|エジプト夢|夢の時代|マチ占断/.test(n) || (/夢/.test(name) && /占/.test(name)))
    return "キーワード抽出→夢辞典マスタ照合（またはLLM補完）。";
  if (/風水|家相|ヴァーストゥ|phong|堪舆/.test(n))
    return "間取り・方位・年命から飛星／八宅等の流派アルゴリズム（設定で切替）。";
  if (/動物占い|五星三心/.test(n))
    return "誕生日→動物タイプ対応表（版固定）。";
  if (/誕生花|花言葉|花弁占い/.test(n))
    return "月日または花種→マスタ照合。";
  if (/演禽/.test(n))
    return "干支・宿・禽星対応表から星決定→古典ルール文案。";
  if (/密教|曼荼羅|タントラ系吉日/.test(n))
    return "修法目的×暦→吉日・本尊テーブル（宗教注記必須）。";
  if (/陰陽道/.test(n))
    return "奇門等サブモジュール呼出しで復元ルール出力。";
  if (/算木|竹籤/.test(n))
    return "乱数で籤ID→短文マスタ。";
  if (/水晶占い|水晶玉|クリスタロ|スクリュー/.test(n))
    return "主観再現困難。演出＋テンプレまたはLLM（再現性低）。";
  if (/チャネリング|守護霊|メンター占い|チャネリング系/.test(n))
    return "LLM＋ペルソナ。免責・監査ログ必須。";
  if (/鉄板神数/.test(n))
    return "四柱→条文番号アルゴリズム＋条文DB。";
  if (/河洛理数/.test(n))
    return "生年月日・画数から先天後天卦→易数ルール。";
  if (/皇極経世/.test(n))
    return "長周期数術モデル（簡略版はマクロ運気テキスト）。";
  if (/測字/.test(n))
    return "部首・画数・連想辞書＋任意でLLM補完。";
  if (/鳥占|風角|アーキャン|南インド民俗/.test(n))
    return "鳥・風のカテゴリ入力→オーメンテーブル。";
  if (/ラムル|ラーマル|geomancy|砂占い（サヘル）/.test(n))
    return "4×4点の偶奇（乱数可）→16図形→解釈テーブル。";
  if (/棋占い/.test(n))
    return "盤面ハッシュまたは乱数配置→局所ルールブック。";
  if (/擲筊|杯教|杯珓/.test(n))
    return "2枚コイン的確率で聖杯等をシミュレートし連続ルールで判定。";
  if (/合婚|グナ・ミラン/.test(n))
    return "双方命式→点数化ルール（36点法等）。";
  if (/秤骨/.test(n))
    return "干支ごと重量加算→総量で歌诀マスタ。";
  if (/生肖|属相/.test(n) || /干支年運/.test(n))
    return "生年支×流年支の刑冲合害テーブル。";
  if (/太歳|犯太歳/.test(n))
    return "流年支と生年支の関係フラグ→文案（文化的注記）。";
  if (/納音/.test(n))
    return "年柱干支→納音五行マスタ。";
  if (/七政四余/.test(n))
    return "古典天体位置計算＋中国占星ルール。";
  if (/二十八宿占/.test(n))
    return "暦計算で宿→吉凶マスタ。";
  if (/トジョン/.test(n))
    return "朝鮮命理文献の式をデジタル化（四柱計算前提）。";
  if (/花ペ|花びら/.test(summary || ""))
    return "花弁偶奇または乱数で恋愛テキスト。";
  if (/巫堂|굿|シャーマン|ボー|テングリ|ナバホ|セイズ/.test(n))
    return "儀礼本体は非再現。演出・LLM・シンボル乱択に限定。";
  if (/羊骨|甲骨占い/.test(n))
    return "亀裂画像分類または教育用ランダムシミュレーション。";
  if (/モ（骰子）|モ占い/.test(n))
    return "サイコロ目×質問カテゴリで照合表から行動指南。";
  if (/タイ占星|ไทย|クメール|ラオス仏教暦|ビルマ|プリンボン|ジャワン|パウコン/.test(n))
    return "ローカル暦＋占星／ワウコン等の対応表をデータ化して検索。";
  if (/吉祥番号/.test(n))
    return "数字列→タイ語読み吉凶音テーブル。";
  if (/マレー伝統|民族口承|大洋州島嶼|パシュトゥーン|ベドウィン|北欧金属/.test(n))
    return "兆候・夢タグの地域別辞典（データ収集前提）。";
  if (/アルブラリョ|伝統治療者/.test(n))
    return "症状タグ→説明文。医療免責必須。";
  if (/華人命理/.test(n))
    return "八字モジュール＋風水モジュールの合成。";
  if (/Jyotiṣa|インド占星|ヴェーダ|僧伽罗|イスラム圏内の占星|チベット占星|KPシステム|プラシュナ|ムフルタ/.test(n))
    return "サイデリアル計算・ダシャー・divisional charts 等（専用ライブラリ推奨）。";
  if (/ナーディ/.test(n))
    return "商業条文検索またはLLM（検証性低）。";
  if (/ラトナ|宝石/.test(n))
    return "チャートから吉星凶星判定→推奨石テーブル。";
  if (/カウリ|ディレ・カウリ/.test(n))
    return "貝の表裏ビット列（乱数可）→パターンマスタ。";
  if (/聖典籤|バイブリオ|聖書開き|クルアーン開き|Sortes/.test(n))
    return "テキスト分割し乱数インデックスで節・詩行を返す。";
  if (/ヒジュラ|ペルシャ古暦|エチオピア教会暦|ポリネシア暦/.test(n))
    return "宗教／文化暦マスタで吉日・齋日フラグ。";
  if (/イスラム占星|イルム・ヌジューム/.test(n))
    return "中世イスラム占星テーブル＋エフェメリス（文献ベース）。";
  if (/コーヒー|茶葉占い/.test(n))
    return "残渣形状認識は困難。シンボル選択UIまたはランダム象徴。";
  if (/ジェマトリア/.test(n))
    return "ヘブライ文字→数値換算→スコア辞書。";
  if (/カバラ占い/.test(n))
    return "名前等から生命樹パスを割当（商業ルール固定）。";
  if (/臓器占い|神託（オラクル）|デルポイ/.test(n))
    return "歴史・教育コンテンツ。実データ占断は非推奨。";
  if (/ルーン|オーガム/.test(n))
    return "記号抽選→意味辞典。";
  if (/プレイングカード|トランプ占い/.test(n))
    return "52枚引き→位置意味テーブル。";
  if (/振り子|ペンデュラム/.test(n))
    return "Yes/No UIまたは傾きセンサ／乱数。";
  if (/ダウジング/.test(n))
    return "地図クリック演出で「反応」表示。";
  if (/筆跡|グラフォロジー/.test(n))
    return "画像特徴MLまたは質問票近似。";
  if (/物体霊読|サイコメトリー/.test(n))
    return "演出のみまたはLLM。検証不可。";
  if (/ロマ占い|溶鉛|溶蝋|バルト金属|ウィキル|インボルク/.test(n))
    return "形状シルエット選択または画像分類で象徴文案。";
  if (/イファ|サンテリア|ディラゴゴ|ウンバンダ|カンドンブレ|ヴードゥー/.test(n))
    return "投げ結果ビット列→口承テキストDB。宗教・文化配慮。";
  if (/デカン占星/.test(n))
    return "黄経10度区分で細分テキスト。";
  if (/アカン系/.test(n))
    return "曜日生まれ→魂名・性格テーブル。";
  if (/サカルバ|ナキンガス|サンゴマ|メラネシア骨|ウィスパリング|骨・氷・光/.test(n))
    return "骨配置パターンコード→民族誌辞典。";
  if (/メディスン・ホイール|トーテム|マヤ占星（商業版）|ドリームスペル|13の月の暦/.test(n))
    return "誕生日またはクイズ→タイプ対応表（版固定）。";
  if (/マヤ暦占い|トナルポウアリ|サウンポチュリ/.test(n))
    return "グレゴリ→260/365暦変換（相関定数は設定化）。";
  if (/クルカンドゥ/.test(n))
    return "コカ葉パターン選択→辞典。";
  if (/アヤワスカ/.test(n))
    return "薬物儀礼は実装不可。警告文のみ。";
  if (/ラテンアメリカ都市占星|イラン都市部/.test(n))
    return "西洋占星計算＋言語ローカライズテンプレ。";
  if (/マオリ|ハワイ伝統|オーストラリア先住民占断|夢の時代/.test(n))
    return "文化説明・外部リソース誘導。自動断定は避ける。";
  if (/デジタル御神籤|公式デジタル籤|求籤|フォーチュン|りんご皮|アルファベット占い|サイコロ占い|三枚コイン|花弁|色占い|タイプ診断|スマホ易|天使メッセージ|スプレッドシート|SNSホロスコープ|アプリ内相性|ゲーム占い/.test(n))
    return "乱数または単純式＋マスタテキスト。";
  if (/生成AI占い|対話型占いボット/.test(n))
    return "LLM＋RAG。プロンプト安全策・免責。";
  if (/VTuber/.test(n))
    return "人的配信またはコメント収集のみ。自動占断は別モジュール。";
  if (/ヒューマンデザイン/.test(n))
    return "出生時刻の天体計算→タイプ・権威（公開仕様・ライセンス要確認）。";
  if (/遺伝子占い|DNA/.test(n))
    return "外部ゲノムAPIの結果コード→文案。";
  if (/オーラカメラ/.test(n))
    return "入力値または乱数で色→性格テンプレ。";
  if (/リモート占いサービス/.test(n))
    return "予約・決済・セッションログ。占断ロジックは人的。";
  if (/オンチェーンおみくじ|NFT/.test(n))
    return "VRF等で乱数→トークンURI。";
  if (/扶鸞|ネクロマンシー|頭蓋骨占い|神判・湯占/.test(n))
    return "歴史・倫理説明モード。実装占断は非推奨。";
  if (/易林|太玄|雲占い|炎・灰|黒鏡|香煙占い|アパントマンシー|動物の偶然遭遇/.test(n))
    return "象徴タグまたは環境入力→辞典／教育シミュレータ。";
  if (/音感占い|オノマトマンシー/.test(n))
    return "音韻特徴→スコアテーブル。";
  if (/自動命盤|紫微斗数Web/.test(n))
    return "サーバで命盤計算しJSON/SVG返却。節気・真太陽時のテスト必須。";
  if (/デジタルルノルマン/.test(n))
    return "シャッフル乱数＋カード画像ライセンス管理。";
  if (/占星API連携/.test(n))
    return "外部エフェメリスAPI＋キャッシュ層。";

  return "入力→中間指標→テンプレ文案のパイプライン。マスタはDB化し版管理。";
}

function outputBody(outCat) {
  if (!outCat)
    return "ラベル・説明文・娯楽フラグ・マスタ参照ID等の構造化JSON。";
  return `${outCat}向けの説明テキスト・スコア・推奨アクションを構造化データで返す。`;
}

function implMemo(diffNorm, diffRaw, summary, name) {
  const parts = [];
  if (diffNorm === "難")
    parts.push("流派・節気・TZ仕様を先に固定し黄金データで回帰テストする。");
  if (
    /手の写真|顔写真|画像認識|筆跡|手相|人相|面相/.test(summary || "") ||
    /手相|人相|面相|筆跡|パンガラオ|グラフォロジー/.test(name)
  )
    parts.push("生体情報は同意・用途限定・差別リスクに配慮。");
  if (/宗教|密教|イファ|ヴード|オリシャ|神託|クルアーン|聖典/.test(summary + name))
    parts.push("宗教・民族文化: 娯楽と信仰実践の境界を明示。");
  if (/LLM|チャネリング|生成AI|AI占い/.test(summary + name))
    parts.push("生成AIは免責・ハルシネーション対策・ログ監査。");
  if (!parts.length) parts.push("計算モジュールとマスタデータを分離し版管理する。");
  return parts.join(" ");
}

function sectionForIndex(idx, title) {
  if (idx === 0) return "第1回：東アジア・東南アジア・南アジア";
  if (title.startsWith("テュルク系シャーマン")) return "第2回：中央アジア・中東・ヨーロッパ・アフリカ";
  if (title.startsWith("メディスン・ホイール")) return "第3回：アメリカ大陸・オセアニア・現代・デジタル系";
  if (title.startsWith("亀甲占い")) return "第4回：抜け漏れ補填・横断";
  return null;
}

const text = fs.readFileSync(SRC, "utf8");
const entries = parseEntries(text);
const diffCounts = { 易: 0, 中: 0, 難: 0 };
const out = [];
out.push("# 占い村リサーチ：占いロジック実装メモ", "");
out.push("`01_uranai_list.md` の各エントリに対応し、プログラム実装のための **判定パイプライン** を整理した。", "");
out.push("---", "");

entries.forEach((e, idx) => {
  const sec = sectionForIndex(idx, e.title);
  if (sec) {
    out.push(`## ${sec}`, "");
  }
  const name = e["占い名"] || e.title;
  let diffRaw = e["実装難易度"];
  if (!diffRaw) diffRaw = "中";
  const diff = normalizeDifficulty(diffRaw);
  diffCounts[diff]++;

  const outline = logicOutline(name, e["概要メモ"], e["必要な入力情報"], e["出力カテゴリ"]);
  const body = outputBody(e["出力カテゴリ"]);
  const memo = implMemo(diff, diffRaw, e["概要メモ"], name);

  out.push(`### ${name}`, "");
  out.push("| 項目 | 内容 |", "|------|------|");
  out.push(`| 占い名 | ${name} |`);
  out.push(`| 必要な入力情報 | ${e["必要な入力情報"]} |`);
  out.push(`| 判定ロジック概要 | ${outline} |`);
  out.push(`| 出力内容 | ${body} |`);
  out.push(`| 更新頻度 | ${e["更新頻度"]} |`);
  out.push(`| 実装難易度 | ${diff} |`);
  out.push(`| 実装メモ | ${memo} |`);
  out.push("");
});

out.push("---", "");
out.push("## 難易度集計（`01` の表記を正規化：`難`含む→難、`易`のみ→易、それ以外→中）", "");
out.push(`- **易**: ${diffCounts["易"]} 件`);
out.push(`- **中**: ${diffCounts["中"]} 件`);
out.push(`- **難**: ${diffCounts["難"]} 件`);
out.push(`- **合計**: ${entries.length} 件`);
out.push("");
out.push("再生成する場合: `node research/build_uranai_logic_from_01.mjs`（リポジトリルート想定）。");
out.push("");

fs.writeFileSync(OUT, out.join("\n"), "utf8");
console.log("Wrote", OUT, "entries=", entries.length, diffCounts);
