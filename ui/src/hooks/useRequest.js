import { useCallback } from 'react';
import { useAuth0 } from '@auth0/auth0-react';

const appRoot = (window.location.origin + window.location.pathname).replace(/\/$/, '');
const apiRoot = `${appRoot}/api`;

export default function useRequest() {
  const { getAccessTokenSilently } = useAuth0();

  const requestCallback = useCallback(
    async (path, options) => {
      const token = await getAccessTokenSilently();

      return await fetch(`${apiRoot}${path}`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        ...options,
      });
    },
    [getAccessTokenSilently]
  );

  return requestCallback;
}
