import { useCallback } from 'react';
import { useAuth0 } from '@auth0/auth0-react';

const appRoot = (window.location.origin + window.location.pathname).replace(/\/$/, '');
const apiRoot = `${appRoot}/api`;

export default function useRequest() {
  const { getAccessTokenSilently } = useAuth0();

  const requestCallback = useCallback(
    async (path, options = {}) => {
      const token = await getAccessTokenSilently();
      const headers = {
        Authorization: `Bearer ${token}`,
      };

      // Only set Content-Type to application/json if the body is not FormData
      if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
        // Assuming you want to stringify JSON bodies:
        options.body = JSON.stringify(options.body);
      }

      return await fetch(`${apiRoot}${path}`, {
        ...options,
        headers: {
          ...options.headers,
          ...headers,
        },
      });
    },
    [getAccessTokenSilently]
  );

  return requestCallback;
}
