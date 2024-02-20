import { jwtDecode } from 'jwt-decode';
import { useEffect, useState } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { Router, Route } from "wouter";
import useHashLocation from '../hooks/useHashLocation';
import Spinner from './Spinner';
import Layout from './Layout';
import UploadTranscript from '../views/UploadTranscript';
import DeleteUser from '../views/DeleteUser';
import WelcomePage from './WelcomePage';
import HomePage from './HomePage';

export default function App() {
  const {
    isAuthenticated,
    isLoading,
    loginWithPopup,
    user,
    getAccessTokenSilently
  } = useAuth0();

  const [token, setToken] = useState(null);
  const [location] = useHashLocation();

  useEffect(() => {
    if (isAuthenticated && !isLoading && !token) {
      getAccessTokenSilently().then((token) => setToken(jwtDecode(token)));
    }
  }, [isAuthenticated, isLoading, user]);

  const userFirstName = user && user.name.split(" ")[0];

  if (isLoading) {
    return <Spinner />
  } else if (isAuthenticated) {
    return (
      <Router hook={useHashLocation}>
        <Layout current={location} token={token}>
          <Route path="/">
            <HomePage userFirstName={userFirstName}/>
          </Route>
          <Route path="/upload-transcript" component={UploadTranscript} />
          <Route path="/delete-user" component={DeleteUser} />
        </Layout>
      </Router>
    )
  } else {
    return <WelcomePage loginWithPopup={loginWithPopup} />
  }
}
