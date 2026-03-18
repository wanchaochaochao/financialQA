import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "金融资产问答系统",
  description: "基于 AI 的智能金融数据分析与知识问答平台",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.Node;
}>) {
  return (
    <html lang="zh-CN">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
