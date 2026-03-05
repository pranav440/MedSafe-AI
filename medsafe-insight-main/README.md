# MedSafe AI – Frontend UI

This is the React-based frontend for the MedSafe AI system. It provides real-time patient monitoring, prescription analysis, and intelligent clinical alerts.

## Technologies Used

- **Vite**: Frontend build tool
- **React**: UI library
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: High-quality UI components
- **Recharts**: Data visualization for vitals history

## Getting Started

1.  **Install Dependencies**:
    ```bash
    npm install
    ```

2.  **Run Development Server**:
    ```bash
    npm run dev
    ```

3.  **Environment Variables**:
    By default, the frontend connects to the backend at `http://localhost:5000`. You can override this by setting the `VITE_API_URL` environment variable.

## Features

- **Real-time Vitals Dashboard**: Live updates of patient telemetry.
- **Prescription Analyzer**: Upload and analyze medical prescriptions.
- **Drug Interaction Checker**: Verify safety of multiple medications.
- **Symptom Guidance**: AI-powered symptom analysis.
- **Side-Effect Reporter**: Log and analyze adverse drug reactions.
