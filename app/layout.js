import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

const plusJakarta = Plus_Jakarta_Sans({
  variable: "--font-plus-jakarta",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
});

export const metadata = {
  title: "AI-Based Spam Email Detection | Blockchain Tamper-Proof Logging",
  description:
    "Intelligent email spam detection powered by machine learning with blockchain-based tamper-proof audit logging for enterprise-grade security.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${plusJakarta.variable} antialiased`}>
      <body className="min-h-screen bg-[#050505] text-[#f8fafc] font-[family-name:var(--font-plus-jakarta)]">
        <div className="relative z-10">{children}</div>
      </body>
    </html>
  );
}
