import { useState } from "react";
import useRequest from '../hooks/useRequest';
import Spinner from '../components/Spinner';
import Toast from '../components/Toast';


export default function DeleteUser() {
  const apiRequest = useRequest();
  const [isLoading, setIsLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [searchComplete, setSearchComplete] = useState(false);
  const [user, setUser] = useState(null);
  const [userDeleted, setUserDeleted] = useState(null);
  const [toast, setToast] = useState({
    showToast: false,
    label: null,
    type: null,
  });

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
      setSearchComplete(false);
      setToast({
        type: "error",
        label: "An error occurred while searching for the user.",
        showToast: true,
      });
    }
  };

  const deleteUser = async () => {
    if (user.has_portfolio) {
      setToast({
        type: "warning",
        label: "This user has assets in their portfolio and cannot be deleted.",
        showToast: true,
      });
    } else {
      setUserDeleted(null);

      if (confirm(`Are you sure you want to delete the user "${user.email}"?`)) {
        setIsLoading(true);

        const res = await apiRequest(`/user/${email}`, {
          method: "delete",
        });

        if (res.status === 200) {
          setUserDeleted(user.email);
          setToast({
            type: "success",
            label: `${userDeleted} has been deleted.`,
            showToast: true,
          });
        } else if (res.status !== 404) {
          setToast({
            type: "error",
            label: "An error occurred while deleting the user.",
            showToast: true,
          });
        }

        setEmail("");
        setUser(null);
        setSearchComplete(false);
        setIsLoading(false);
      }
    }
  }

  return (
    <div>
      {toast.showToast && <Toast type={toast.type} label={toast.label} onClose={() => setToast(previous => ({ ...previous, showToast: false }))} />}
      <div className="flex flex-col gap-y-3">
        <label htmlFor="email" className="block text-sm font-medium leading-6 text-white">
          User Email
        </label>
        <input
          id="email"
          type="email"
          value={email} onChange={e => handleChange(e.target.value)}
          className="block max-w-sm w-full rounded-md border-0 px-3 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
          placeholder="you@example.com"
        />
        <div>
          <button
            type="button"
            onClick={() => search()}
            className="rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-[#4654A3] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
          >
            Search
          </button>
        </div>
      </div>
      {isLoading && <div><Spinner /></div>}
      {!isLoading && searchComplete && !user && <div className="mt-2"><p className="text-sm text-red-600">No user found with that email.</p></div>}
      {!isLoading && searchComplete && user &&
        <table className="w-full divide-y divide-gray-300">
          <thead>
            <tr>
              <th
                scope="col"
                className="py-3.5 pr-5 text-left text-sm font-semibold text-white"
              >
                Email
              </th>
              <th
                scope="col"
                className="py-3.5 pr-5 text-left text-sm font-semibold text-white"
              >
                Name
              </th>
              <th
                scope="col"
                className="py-3.5 text-left text-sm font-semibold text-white"
              >

              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            <tr>
              <td className="py-4 pr-5 text-sm text-white">{user.email}</td>
              <td className="py-4 pr-5 text-sm text-white">{user.name || "N/A"}</td>
              <td className="py-4 text-sm text-white text-right">
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
    </div>
  );
};
