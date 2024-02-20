import { useState, useEffect } from "react";
import useRequest from '../../hooks/useRequest';
import Spinner from '../../components/Spinner';
import { Link } from "wouter";

export default function BrassicaOfferings() {
  const apiRequest = useRequest();

  const [isLoadingOfferings, setIsLoadingOfferings] = useState(true);
  const [offerings, setOfferings] = useState([]);

  useEffect(() => {
    async function fetchData() {
      setIsLoadingOfferings(true);

      const res = await apiRequest("/brassica/offerings", {
        method: "get",
      });

      if (res.status === 200) {
        const data = await res.json();
        setOfferings(data.sort((a, b) => a.attributes.title.localeCompare(b.attributes.title)));
      } else {
        alert("An error occurred while loading offerings.");
      }

      setIsLoadingOfferings(false);
    }

    if (offerings.length === 0) {
      fetchData();
    }
  }, []);

  if (isLoadingOfferings) {
    return <Spinner message="Loading offerings…" />;
  }

  return (
    <div>
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-base font-semibold leading-6 text-gray-900">Brassica Offerings</h1>
          <p className="mt-2 text-sm text-gray-700">
            Create or manage an existing offering to add or remove assets.
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <Link
            href="/brassica-offerings/new"
            className="block rounded-md bg-blue-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
          >
            Create Offering
          </Link>
        </div>
      </div>
      <div className="mt-8 flow-root">
        <div className="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
            <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
              <table className="min-w-full divide-y divide-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">
                      Title
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Description
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Status
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Dates
                    </th>
                    <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {offerings.map((offering) => (
                    <tr key={offering.id}>
                      <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">{offering.attributes.title}</td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{offering.attributes.description}</td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{offering.attributes.status}</td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{offering.attributes.targetStartDate} to {offering.attributes.targetTerminationDate}</td>
                      <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                        <div className="flex gap-4 justify-end">
                          <Link href={`/brassica-offerings/${offering.id}/edit`} className="text-blue-600 hover:text-blue-900">
                            Edit
                          </Link>
                          <Link href={`/brassica-offerings/${offering.id}/assets`} className="text-blue-600 hover:text-blue-900">
                            Manage Assets
                          </Link>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
};
