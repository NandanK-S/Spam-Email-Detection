import test, { describe } from "node:test";
import assert from "node:assert/strict";

import {
  predictEmail,
  getBlockchainLog,
  verifyChain,
  getModelComparison,
} from "./api.js";

describe("Frontend API Client (api.js)", () => {
  const originalFetch = global.fetch;

  test("predictEmail returns data on 200 OK", async () => {
    const mockResponse = {
      prediction: "Spam",
      confidence: 0.99,
      emailHash: "0xabc",
      blockNumber: 1,
      features: { charCount: 20 },
    };

    global.fetch = async (url, options) => {
      assert.equal(url, "/api/predict");
      assert.equal(options.method, "POST");
      assert.equal(JSON.parse(options.body).text, "Test email");
      return {
        ok: true,
        status: 200,
        json: async () => mockResponse,
      };
    };

    const res = await predictEmail("Test email");
    assert.deepEqual(res, mockResponse);
  });

  test("predictEmail throws structured error on 400 Bad Request", async () => {
    global.fetch = async () => {
      return {
        ok: false,
        status: 400,
        json: async () => ({ detail: "Email text cannot be empty" }),
      };
    };

    await assert.rejects(
      async () => await predictEmail(""),
      /Email text cannot be empty/
    );
  });

  test("predictEmail falls back to generic message if json parsing fails", async () => {
    global.fetch = async () => {
      return {
        ok: false,
        status: 503,
        json: async () => {
          throw new Error("Invalid JSON");
        },
      };
    };

    await assert.rejects(
      async () => await predictEmail("hello"),
      /Prediction failed/
    );
  });

  test("getBlockchainLog returns block list", async () => {
    const mockBlocks = [
      { blockNumber: 1, prediction: "Spam", confidence: 0.95 },
      { blockNumber: 2, prediction: "Ham", confidence: 0.91 },
    ];

    global.fetch = async (url) => {
      assert.equal(url, "/api/blockchain/log");
      return {
        ok: true,
        status: 200,
        json: async () => mockBlocks,
      };
    };

    const res = await getBlockchainLog();
    assert.deepEqual(res, mockBlocks);
  });

  test("getBlockchainLog throws error on HTTP error", async () => {
    global.fetch = async () => ({
      ok: false,
      status: 500,
    });

    await assert.rejects(
      async () => await getBlockchainLog(),
      /Failed to fetch blockchain log/
    );
  });

  test("verifyChain sends simulate_tamper flag accurately", async () => {
    global.fetch = async (url, options) => {
      assert.equal(url, "/api/blockchain/verify");
      assert.equal(options.method, "POST");
      const body = JSON.parse(options.body);
      assert.equal(body.simulate_tamper, true);
      return {
        ok: true,
        status: 200,
        json: async () => ({ valid: false, tampered_block: 2 }),
      };
    };

    const res = await verifyChain(true);
    assert.equal(res.valid, false);
    assert.equal(res.tampered_block, 2);
  });

  test("verifyChain throws error on failure", async () => {
    global.fetch = async () => ({
      ok: false,
      status: 503,
    });

    await assert.rejects(
      async () => await verifyChain(),
      /Chain verification failed/
    );
  });

  test("getModelComparison returns comparison models", async () => {
    const mockModels = [
      { name: "Random Forest", f1Score: 0.9685, selected: true },
    ];

    global.fetch = async (url) => {
      assert.equal(url, "/api/models/comparison");
      return {
        ok: true,
        status: 200,
        json: async () => mockModels,
      };
    };

    const res = await getModelComparison();
    assert.deepEqual(res, mockModels);
  });

  test("getModelComparison throws on failure", async () => {
    global.fetch = async () => ({
      ok: false,
      status: 500,
    });

    await assert.rejects(
      async () => await getModelComparison(),
      /Failed to fetch model comparison/
    );
  });

  // Restore fetch
  test.after(() => {
    global.fetch = originalFetch;
  });
});

