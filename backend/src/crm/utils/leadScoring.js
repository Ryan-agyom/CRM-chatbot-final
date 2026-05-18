export function scoreLead({ budget = 0, interestLevel = 0, companySize = 0, purchaseTimeline = 0 }) {
  return Math.min(
    100,
    Number(budget) * 0.0005 +
      Number(interestLevel) * 20 +
      Number(companySize) * 2 +
      Math.max(0, 30 - Number(purchaseTimeline))
  );
}
