import { jwtDecode } from 'jwt-decode';
import { useEffect, useState } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { Router, Route } from "wouter";
import useHashLocation from '../hooks/useHashLocation';
import Spinner from './Spinner';
import Layout from './Layout';
import Logo from './Logo';
import WelcomePage from '../views/WelcomePage';
import UploadTranscript from '../views/UploadTranscript';
// import ArtistImages from '../views/ArtistImages';
// import DeleteUser from '../views/DeleteUser';
// import BrassicaOfferings from '../views/BrassicaOfferings';
// import CreateBrassicaOffering from '../views/CreateBrassicaOffering';
// import EditBrassicaOffering from '../views/EditBrassicaOffering';
// import BrassicaSecurities from '../views/BrassicaSecurities';
// import CreateBrassicaSecurity from '../views/CreateBrassicaSecurity';

export default function App() {
  const {
    isAuthenticated,
    isLoading,
    loginWithPopup,
    user,
    logout,
    getAccessTokenSilently
  } = useAuth0();

  const [token, setToken] = useState(null);
  const [location] = useHashLocation();

  useEffect(() => {
    if (isAuthenticated && !isLoading && !token) {
      getAccessTokenSilently().then((token) => setToken(jwtDecode(token)));
    }
  }, [isAuthenticated, isLoading, user]);

  if (isLoading) {
    return <Spinner />
  } else if (isAuthenticated) {
    return <Router hook={useHashLocation}>
      <Layout current={location} token={token} >
        <Route path="/welcome" component={WelcomePage} />
        <Route path="/upload-transcript" component={UploadTranscript} />
      </Layout>
    </Router>
  } else {
    return <div className="h-full w-full flex flex-col items-center justify-center gap-16">
      <Logo className="h-8 w-auto" />
      <button
        onClick={() => loginWithPopup()}
        className="rounded-md bg-blue-600 px-5 py-2.5 text-lg font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
      >
        Sign in
      </button>
    </div>
  }
}
