import { useState, useEffect } from "react";
import useRequest from '../hooks/useRequest';
import Spinner from '../components/Spinner';
import { Link } from "wouter";

export default function BrassicaSecurities(props) {
  const apiRequest = useRequest();

  const [isLoadingOffering, setIsLoadingOffering] = useState(true);
  const [offering, setOffering] = useState(null);
  const [offeringSeries, setOfferingSeries] = useState([]);

  useEffect(() => {
    async function fetchData() {
      setIsLoadingOffering(true);

      let res = await apiRequest(`/brassica/offering/${props.params.id}`, {
        method: "get",
      });

      if (res.status === 200) {
        const data = await res.json();
        setOffering(data);
      } else {
        alert("An error occurred while loading the offering.");
      }

      res = await apiRequest(`/brassica/offering/${props.params.id}/series`, {
        method: "get",
      });

      if (res.status === 200) {
        const data = await res.json();
        setOfferingSeries(data.sort((a, b) => a.attributes.title.localeCompare(b.attributes.title)));
      } else {
        alert("An error occurred while loading the offering series.");
      }

      setIsLoadingOffering(false);
    }

    if (offering === null) {
      fetchData();
    }
  }, []);

  const removeAsset = async (id) => {
    if (!confirm("Are you sure you want to remove this asset from the offering?")) {
      return;
    }

    setIsLoadingOffering(true);

    const res = await apiRequest(`/brassica/offering/${props.params.id}/series/${id}`, {
      method: "delete",
    });

    if (res.status === 200) {
      const data = await res.json();
      setOfferingSeries(data.sort((a, b) => a.attributes.title.localeCompare(b.attributes.title)));
    } else {
      alert("An error occurred while removing the asset.");
    }

    setIsLoadingOffering(false);
  };

  if (isLoadingOffering) {
    return <Spinner message="Loading offering…" />;
  }

  return (
    <div>
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-base font-semibold leading-6 text-gray-900">Brassica Offering: {offering.attributes.title}</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage assets associated with this offering.
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none flex gap-4">
          <Link
            href={`/brassica-offerings`}
            className="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
          >
            Back
          </Link>
          <Link
            href={`/brassica-offerings/${props.params.id}/assets/new`}
            className="block rounded-md bg-blue-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
          >
            Associate Asset
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
                      Unit Price
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Units for Sale
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Units Purchased
                    </th>
                    <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {offeringSeries.map((offeringSeries) => (
                    <tr key={offeringSeries.id}>
                      <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">{offeringSeries.attributes.title}</td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{offeringSeries.attributes.purchasePricePerUnit}</td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{offeringSeries.attributes.totalUnitsForSale}</td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{offeringSeries.attributes.totalUnitsPurchased}</td>
                      <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                        <button onClick={() => removeAsset(offeringSeries.id)} className="cursor-pointer text-red-600 hover:text-red-900">
                          Remove
                        </button>
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
