import React from 'react'
import ReactDOM from 'react-dom/client'
import { Auth0Provider } from '@auth0/auth0-react';
import { UploadTranscriptContextProvider } from './context/UploadTranscriptContext';
import App from './components/App'
import './index.css'

const appRoot = (window.location.origin + window.location.pathname).replace(/\/$/, '');

const identityProvider = {
  domain: __AUTH0_DOMAIN__,
  clientId: __AUTH0_CLIENT_ID__,
};

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Auth0Provider
      domain={identityProvider.domain}
      clientId={identityProvider.clientId}
      authorizationParams={{
        redirect_uri: appRoot,
        audience: __AUTH0_AUDIENCE__
      }}
    >
        <UploadTranscriptContextProvider>
          <App />
        </UploadTranscriptContextProvider>
    </Auth0Provider>
  </React.StrictMode>,
)
