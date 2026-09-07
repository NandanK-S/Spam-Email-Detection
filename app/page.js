"use client";

import { useState, useEffect } from "react";

import Header from "./components/Header";
import EmailInputForm from "./components/EmailInputForm";
import PredictionResult from "./components/PredictionResult";
import FeatureBreakdownTable from "./components/FeatureBreakdownTable";
import BlockchainLog from "./components/BlockchainLog";
import ChainVerifyPanel from "./components/ChainVerifyPanel";
import ModelComparisonCard from "./components/ModelComparisonCard";

import { predictEmail, getBlockchainLog } from "./lib/api";

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [predictionResult, setPredictionResult] = useState(null);
  const [blockchainLog, setBlockchainLog] = useState([]);

  // Load initial blockchain log on mount
  useEffect(() => {
    getBlockchainLog()
      .then((log) => setBlockchainLog(log))
      .catch(() => setBlockchainLog([]));
  }, []);

  const handleCheckEmail = async (text) => {
    setIsLoading(true);
    setPredictionResult(null);

    try {
      const result = await predictEmail(text);
      setPredictionResult(result);

      // Refresh blockchain log from backend (all predictions are logged)
      const updatedLog = await getBlockchainLog();
      setBlockchainLog(updatedLog);
    } catch (err) {
      console.error("Prediction error:", err);
      setPredictionResult({
        prediction: "Error",
        confidence: 0,
        features: null,
        error: err.message,
      });
    } finally {
      setIsLoading(false);
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
