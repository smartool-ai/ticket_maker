import { useState } from "react";
import useRequest from '../hooks/useRequest';
import Spinner from '../components/Spinner';
import Notice from '../components/Notice';

export default function DeleteUser() {
  const apiRequest = useRequest();

  const [isLoading, setIsLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [searchComplete, setSearchComplete] = useState(false);
  const [user, setUser] = useState(null);
  const [userDeleted, setUserDeleted] = useState(null);

  const handleChange = (value) => {
    setEmail(value);
    setUser(null);
    setSearchComplete(false);
  };

  const search = async () => {
    setUser(null);
    setSearchComplete(false);
    setIsLoading(true);
    setUserDeleted(null);

    const res = await apiRequest(`/user/${email}`, {
      method: "get",
    });

    setSearchComplete(true);
    setIsLoading(false);

    if (res.status === 200) {
      setUser(await res.json());
    } else if (res.status !== 404) {
      alert("An error occurred while searching for the user.");
      setSearchComplete(false);
    }
  };

  const deleteUser = async () => {
    if (user.has_portfolio) {
      alert("This user has assets in their portfolio and cannot be deleted.");
    } else {
      setUserDeleted(null);

      if (confirm(`Are you sure you want to delete the user "${user.email}"?`)) {
        setIsLoading(true);

        const res = await apiRequest(`/user/${email}`, {
          method: "delete",
        });

        if (res.status === 200) {
          setUserDeleted(user.email);
        } else if (res.status !== 404) {
          alert("An error occurred while deleting the user.");
        }

        setEmail("");
        setUser(null);
        setSearchComplete(false);
        setIsLoading(false);
      }
    }
  }

  return <div>
    <div className="mb-10">
      <label htmlFor="email" className="block text-sm font-medium leading-6 text-gray-900">
        User Email
      </label>
      <div className="mt-2">
        <input
          id="email"
          type="email"
          value={email} onChange={e => handleChange(e.target.value)}
          className="block max-w-sm w-full rounded-md border-0 px-3 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
          placeholder="you@example.com"
        />
      </div>
      <div className="mt-2">
        <button
          type="button"
          onClick={() => search()}
          className="rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
        >
          Search
        </button>
      </div>
    </div>

    {userDeleted && <Notice>{userDeleted} has been deleted.</Notice>}

    {isLoading && <div><Spinner /></div>}

    {!isLoading && searchComplete && !user && <div className="mt-2"><p className="text-sm text-red-600">No user found with that email.</p></div>}

    {!isLoading && searchComplete && user &&
      <table className="w-full divide-y divide-gray-300">
        <thead>
          <tr>
            <th
              scope="col"
              className="py-3.5 pr-5 text-left text-sm font-semibold text-gray-900"
            >
              Email
            </th>
            <th
              scope="col"
              className="py-3.5 pr-5 text-left text-sm font-semibold text-gray-900"
            >
              Name
            </th>
            <th
              scope="col"
              className="py-3.5 text-left text-sm font-semibold text-gray-900"
            >

            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          <tr>
            <td className="py-4 pr-5 text-sm text-gray-500">
              {user.email}
            </td>
            <td className="py-4 pr-5 text-sm text-gray-500">
              {user.name || "N/A"}
            </td>
            <td className="py-4 text-sm text-gray-500 text-right">
              <button
                type="button"
                onClick={() => deleteUser()}
                className={`rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600 ${user.has_portfolio && 'opacity-50'}`}
              >
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    }
  </div>;
};
