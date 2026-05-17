/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  corePlugins: {
    // MUI + Emotion own base styles; avoids fighting Preflight/normalize resets.
    preflight: false,
  },
  theme: {
    container: {
      center: true,
      padding: {
        DEFAULT: "1rem",
        sm: "1.5rem",
        lg: "2rem",
      },
    },
    extend: {
      fontFamily: {
        sans: ["Roboto", "system-ui", "sans-serif"],
      },
      colors: {
        reader: {
          teal: "#15616d",
          cream: "#ffecd1",
          muted: "#f0f0f0",
        },
      },
    },
  },
  plugins: [],
};
