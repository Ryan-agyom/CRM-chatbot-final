import test from "node:test";
import assert from "node:assert/strict";
import { scoreLead } from "../src/crm/utils/leadScoring.js";

test("lead scoring returns a bounded score", () => {
  const result = scoreLead({
    budget: 70000,
    interestLevel: 4,
    companySize: 50,
    purchaseTimeline: 7
  });

  assert.equal(result, 100);
});
