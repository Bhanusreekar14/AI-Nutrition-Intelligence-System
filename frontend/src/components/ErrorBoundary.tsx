import { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RotateCw } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallbackTitle?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Unhandled UI Render Error caught by ErrorBoundary:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: '60vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '2rem',
          background: 'var(--bg-page)'
        }}>
          <div className="app-card" style={{
            maxWidth: '520px',
            width: '100%',
            padding: '2rem',
            textAlign: 'center',
            borderLeft: '5px solid #e11d48'
          }}>
            <div style={{
              display: 'inline-flex',
              background: '#ffe4e6',
              color: '#e11d48',
              padding: '0.85rem',
              borderRadius: '12px',
              marginBottom: '1rem'
            }}>
              <AlertTriangle size={32} />
            </div>

            <h2 style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
              {this.props.fallbackTitle || 'Something went wrong rendering this page'}
            </h2>

            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
              {this.state.error?.message || 'An unexpected rendering error occurred. Please refresh or try again.'}
            </p>

            <button
              type="button"
              onClick={this.handleReset}
              className="btn-primary"
              style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', margin: '0 auto' }}
            >
              <RotateCw size={16} /> Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
