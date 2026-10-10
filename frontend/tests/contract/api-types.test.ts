import { describe, expect, it } from "vitest";

import type { paths } from "../../src/lib/api/generated";

describe("generated API contract", () => {
  it("contains the health operation", () => {
    const path: keyof paths = "/api/v1/health";
    expect(path).toBe("/api/v1/health");
  });
});
