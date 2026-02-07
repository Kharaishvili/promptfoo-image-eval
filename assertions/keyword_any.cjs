function keywordAny(output, context) {
  const t = String(output ?? "").toLowerCase();
  const keywords = String(context?.vars?.keywords ?? "")
    .toLowerCase()
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);

  const pass = keywords.length > 0 && keywords.some((k) => t.includes(k));

  return {
    pass,
    score: pass ? 1 : 0,
    reason: pass ? "keyword found" : "keyword missing",
  };
}

module.exports = { keywordAny };
