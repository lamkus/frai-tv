import React from 'react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    // send to analytics / Sentry in future
    console.error('ErrorBoundary caught', error, info);
  }

  render() {
    if (this.state.hasError) {
      const isDev = import.meta.env?.DEV;
      const errorMessage = this.state.error?.message;
      const errorStack = this.state.error?.stack;

      return (
        <div className="min-h-screen flex items-center justify-center px-4">
          <div className="text-center max-w-lg">
            <div className="text-6xl mb-4">😵‍💫</div>
            <h2 className="text-fluid-2xl font-semibold mb-2">Etwas ist schiefgelaufen</h2>
            <p className="text-fluid-base text-retro-muted mb-6">
              Ein unerwarteter Fehler hat die Anwendung unterbrochen. Bitte laden Sie die Seite neu
              oder versuchen Sie es später erneut.
            </p>
            <button onClick={() => window.location.reload()} className="btn btn-primary">
              Neu laden
            </button>
            {isDev && (errorMessage || errorStack) && (
              <details className="mt-6 bg-retro-dark/60 border border-retro-gray/40 rounded-lg text-left p-4">
                <summary className="cursor-pointer text-accent-cyan mb-2">
                  Fehlermeldung anzeigen
                </summary>
                <pre className="text-xs whitespace-pre-wrap text-left text-retro-muted overflow-auto max-h-64">
                  {errorMessage}
                  {'\n\n'}
                  {errorStack}
                </pre>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
