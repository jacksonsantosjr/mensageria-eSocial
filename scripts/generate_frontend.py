import os

BASE = r"c:\Users\jackson.junior\Documents\Antigravity\Mensageria eSocial\frontend"

pkg_json = """{
  "name": "esocial-mensageria-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@tanstack/react-query": "^5.0.0",
    "axios": "^1.6.0",
    "clsx": "^2.1.0",
    "lucide-react": "^0.300.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.22.0",
    "tailwind-merge": "^2.2.0"
  },
  "devDependencies": {
    "@tailwindcss/vite": "^4.0.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "tailwindcss": "^4.0.0",
    "typescript": "^5.2.2",
    "vite": "^5.0.0"
  }
}"""

vite_config = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})"""

tsconfig = """{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}"""

tsconfig_node = """{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}"""

index_html = """<!DOCTYPE html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>eSocial Mensageria</title>
  </head>
  <body class="antialiased text-gray-900 bg-gray-50">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>"""

index_css = """@import "tailwindcss";
@theme {
  --color-primary-50: #eff2ff;
  --color-primary-100: #dle3ff;
  --color-primary-200: #b4fbff;
  --color-primary-300: #89e4ff;
  --color-primary-400: #64ccff;
  --color-primary-500: #3eb8ff;
  --color-primary-600: #2d9bd5;
  --color-primary-700: #1b7bcb;
  --color-primary-800: #0f589a;
  --color-primary-900: #063977;
}"""

main_tsx = """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)"""

app_tsx = """import { BrowserRouter as Router } from 'react-router-dom';

function App() {
  return (
    <Router>
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-primary-600 mb-4">eSocial Mensageria</h1>
          <p className="text-gray-600 text-lg">Frontend React + Vite com Tailwind v4 iniciado com sucesso!</p>
        </div>
      </div>
    </Router>
  );
}

export default App;"""

files = {
    "package.json": pkg_json,
    "vite.config.ts": vite_config,
    "tsconfig.json": tsconfig,
    "tsconfig.node.json": tsconfig_node,
    "index.html": index_html,
    "src/index.css": index_css,
    "src/main.tsx": main_tsx,
    "src/App.tsx": app_tsx
}

for filepath, content in files.items():
    full_path = os.path.join(BASE, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as d:
        d.write(content)

print("FRONTEND GERADO!")
