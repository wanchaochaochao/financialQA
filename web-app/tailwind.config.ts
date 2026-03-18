import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Dark theme colors - Financial luxury style
        background: "var(--background)",
        foreground: "var(--foreground)",

        // Custom dark theme palette
        dark: {
          bg: {
            primary: '#0a0a0a',      // 主背景 - 极深黑
            secondary: '#111111',     // 次级背景 - 深黑
            tertiary: '#1a1a1a',      // 三级背景 - 深灰
            elevated: '#1e1e1e',      // 卡片/面板 - 稍亮深灰
            hover: '#252525',         // 悬停状态 - 亮灰
          },
          border: {
            DEFAULT: '#2a2a2a',       // 默认边框 - 深灰
            light: '#333333',         // 亮边框 - 中灰
            accent: '#404040',        // 强调边框
          },
          text: {
            primary: '#e5e7eb',       // 主文字 - 浅灰
            secondary: '#9ca3af',     // 次要文字 - 中灰
            tertiary: '#6b7280',      // 三级文字 - 暗灰
            muted: '#4b5563',         // 弱化文字
          },
          accent: {
            blue: '#0a7ea4',          // 深蓝（金融风格）
            'blue-light': '#1a4d6f',  // 深蓝灰
            gold: '#c9a860',          // 深金色（低调奢华）
            'gold-dark': '#b8860b',   // 暗金色
            teal: '#0d9488',          // 深青色
            slate: '#334155',         // 深石板蓝
          }
        },
      },
    },
  },
  plugins: [],
};
export default config;
