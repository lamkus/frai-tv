# Frontend

This directory contains the skeleton of the frontend application for your custom
video streaming portal. It is built using **React** and **Vite** for rapid
development and easy hot–reloading. The current implementation provides a
minimal example that fetches a list of videos from the backend and displays
them on the page. This is only a starting point—developers are expected to
extend and replace this code with a fully‑fledged user interface that meets
the project requirements defined in the Lastenheft and Pflichtenheft.

## Project structure

- `package.json` – Declares dependencies and scripts for development and
  production builds.
- `vite.config.js` – Configures the Vite development server and defines a
  proxy to the backend API (default port `4000`).
- `src/main.jsx` – Entry point that mounts the React application.
- `src/App.jsx` – Skeleton component that fetches and renders video data.

## Getting started

To develop the frontend locally:

1. Make sure you have Node.js installed (version 18 or later recommended).
2. Install dependencies:

   ```bash
   cd coding_team_workspace/code/frontend
   npm install
   ```

3. Start the development server:

   ```bash
   npm run dev
   ```

4. Open [http://localhost:5173](http://localhost:5173) in your browser. The
   frontend proxies requests to `/api/*` to `http://localhost:4000` by
   default (configured in `vite.config.js`), so ensure the backend server is
   running on port 4000 or adjust the proxy target accordingly.

5. Modify `src/App.jsx` and other files to implement the design and
   functionality described in the project documentation.

## Building for production

To build the frontend for production, run:

```bash
npm run build
```

The optimized static assets will be placed in the `dist` directory. You can
serve these files using any static file server or integrate them into your
backend server.

## Notes

This project is intentionally lightweight and unopinionated to provide a clean
starting point. Feel free to integrate additional libraries such as
`react-router-dom` for routing, `tailwindcss` for styling, or state
management solutions like Redux if needed. Ensure that any dependencies you
add are documented and justified in the technical documentation.