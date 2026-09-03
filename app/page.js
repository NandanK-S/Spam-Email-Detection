"use client";

import { useState, useEffect } from "react";

import Header from "./components/Header";
import EmailInputForm from "./components/EmailInputForm";
import PredictionResult from "./components/PredictionResult";
import FeatureBreakdownTable from "./components/FeatureBreakdownTable";
import BlockchainLog from "./components/BlockchainLog";
import ChainVerifyPanel from "./components/ChainVerifyPanel";
import ModelComparisonCard from "./components/ModelComparisonCard";

import { mockPredictEmail, mockGetBlockchainLog } from "../mock/mockApi";

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [predictionResult, setPredictionResult] = useState(null);
  const [blockchainLog, setBlockchainLog] = useState([]);

  // Load initial blockchain log on mount
  useEffect(() => {
    mockGetBlockchainLog().then((log) => setBlockchainLog(log));
  }, []);

  const handleCheckEmail = async (text) => {
    setIsLoading(true);
    setPredictionResult(null);

    const result = await mockPredictEmail(text);
    setPredictionResult(result);
    setIsLoading(false);

    // If spam, prepend to blockchain log
    if (result.prediction === "Spam") {
      const newBlock = {
        blockNumber: blockchainLog.length + 1,
        timestamp: new Date().toISOString().replace("T", " ").slice(0, 19),
        emailHash: result.emailHash,
        prediction: result.prediction,
        confidence: result.confidence,
      };
      setBlockchainLog((prev) => [newBlock, ...prev]);
    }
  };

  return (
    <main className="min-h-screen">
      <Header />

      <div className="py-8 md:py-12">
        <EmailInputForm onSubmit={handleCheckEmail} isLoading={isLoading} />
      </div>

      {predictionResult && (
        <div>
          <PredictionResult result={predictionResult} />
          <FeatureBreakdownTable features={predictionResult.features} />
        </div>
      )}

      <BlockchainLog blocks={blockchainLog} />

      <ChainVerifyPanel />

      <ModelComparisonCard />

      {/* Footer */}
      <footer className="border-t border-white/[0.04] py-8 text-center">
        <p className="text-xs text-[#64748b]">
          AI-Based Spam Email Detection — Blockchain Tamper-Proof Logging
        </p>
        <p className="text-[10px] text-[#475569] mt-1">
          Major Project • 7th Semester • 2025
        </p>
      </footer>
    </main>
  );
}
