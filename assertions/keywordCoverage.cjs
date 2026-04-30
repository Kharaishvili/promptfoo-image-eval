function keywordCoverage(output, context) {
  const t = String(output ?? "").toLowerCase();
  const keywords = String(context?.vars?.keywords ?? "")
    .toLowerCase()
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  const minKeywords = Math.max(
    1,
    Number.parseInt(context?.vars?.minKeywords ?? "1", 10) || 1,
  );
  const matched = keywords.filter((k) => t.includes(k));

  const pass = keywords.length > 0 && matched.length >= minKeywords;

  return {
    pass,
    score: keywords.length > 0 ? matched.length / keywords.length : 0,
    reason: pass
      ? `matched ${matched.length}/${keywords.length} keywords: ${matched.join(", ")}`
      : `matched ${matched.length}/${keywords.length} keywords; need ${minKeywords}`,
  };
}

module.exports = { keywordCoverage };
