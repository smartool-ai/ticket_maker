import { useState, useRef, useEffect } from "react";
import useRequest from '../hooks/useRequest';
import Spinner from '../components/Spinner';
import { useLocation } from "wouter";
import { Link } from "wouter";

export default function EditBrassicaOffering(props) {
  const apiRequest = useRequest();
  const formRef = useRef(null);
  const [attributes, setAttributes] = useState(null);
  const [offering, setOffering] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoadingOffering, setIsLoadingOffering] = useState(true);
  const [, setLocation] = useLocation();

  useEffect(() => {
    async function fetchData() {
      setIsLoadingOffering(true);

      const res = await apiRequest(`/brassica/offering/${props.params.id}`, {
        method: "get",
      });

      if (res.status === 200) {
        const data = await res.json();
        setOffering(data);
        setAttributes({
          "status": data.attributes.status,
        });
      } else {
        alert("An error occurred while loading the offering.");
      }

      setIsLoadingOffering(false);
    }

    if (attributes === null) {
      fetchData();
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    setIsSaving(true);

    const res = await apiRequest(`/brassica/offering/${props.params.id}`, {
      method: "put",

      body: JSON.stringify({
        status: attributes.status,
      })
    });

    if (res.status === 200) {
      setLocation("/brassica-offerings");
    } else {
      alert("An error occurred while saving the offering.");
    }

    setIsSaving(false);
  };

  if (isLoadingOffering) {
    return <Spinner message="Loading offering…" />;
  }

  if (isSaving) {
    return <Spinner message="Saving offering…" />;
  }

  return <form ref={formRef} onSubmit={handleSubmit}>
    <div className="sm:flex sm:items-center mb-6">
      <div className="sm:flex-auto">
        <h1 className="text-base font-semibold leading-6 text-gray-900">Brassica Offering: {offering.attributes.title}</h1>
        <p className="mt-2 text-sm text-gray-700">
          Update the offering settings.
        </p>
      </div>
      <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none flex gap-4">
        <Link
          href={`/brassica-offerings`}
          className="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
        >
          Back
        </Link>
      </div>
    </div>
    <div className="grid md:grid-cols-2 gap-6 mb-6">
      <div>
        <label htmlFor="status" className="block text-sm font-medium leading-6 text-gray-900">
          Status
        </label>
        <div className="mt-2">
          <select
            id="status"
            value={attributes.status}
            onInput={e => setAttributes({ ...attributes, status: e.target.value })}
            className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
            required
          >
            <option value="draft">draft</option>
            <option value="open">open</option>
          </select>
        </div>
      </div>
    </div>
    <button
      type="submit"
      className="block rounded-md bg-blue-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
    >
      Save Offering
    </button>
  </form>;
};
