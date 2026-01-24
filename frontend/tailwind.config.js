/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                border: "hsl(214.3 31.8% 91.4%)",
                input: "hsl(214.3 31.8% 91.4%)",
                ring: "hsl(243.2 75% 59%)",
                background: "hsl(0 0% 100%)",
                foreground: "hsl(222.2 84% 4.9%)",
                primary: {
                    DEFAULT: "#6366F1", // indigo-500
                    foreground: "#FFFFFF",
                },
                secondary: {
                    DEFAULT: "hsl(210 40% 96.1%)",
                    foreground: "hsl(222.2 47.4% 11.2%)",
                },
                destructive: {
                    DEFAULT: "#EF4444", // red-500
                    foreground: "#FFFFFF",
                },
                muted: {
                    DEFAULT: "#F3F4F6", // gray-100
                    foreground: "#6B7280", // gray-500
                },
                accent: {
                    DEFAULT: "#F3F4F6",
                    foreground: "#111827",
                },
                card: {
                    DEFAULT: "#FFFFFF",
                    foreground: "#111827",
                },
                sidebar: {
                    DEFAULT: "#1E293B", // slate-800
                    foreground: "#E2E8F0", // slate-200
                },
            },
            borderRadius: {
                lg: "0.75rem",
                md: "0.5rem",
                sm: "0.375rem",
            },
        },
    },
    plugins: [],
}
