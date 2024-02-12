import { useState, useRef, useEffect } from "react";
import useRequest from '../hooks/useRequest';
import Spinner from '../components/Spinner';
import { useLocation } from "wouter";
import { Link } from "wouter";

export default function CreateBrassicaOffering(props) {
  const apiRequest = useRequest();

  const formRef = useRef(null);

  const [attributes, setAttributes] = useState({
    "asset_id": "",
  });

  const [isSaving, setIsSaving] = useState(false);

  const [isLoadingAssets, setIsLoadingAssets] = useState(true);
  const [assets, setAssets] = useState([]);
  const [offering, setOffering] = useState(null);

  const [, setLocation] = useLocation();

  useEffect(() => {
    async function fetchData() {
      setIsLoadingAssets(true);

      let res = await apiRequest("/asset", {
        method: "get",
      });

      if (res.status === 200) {
        const data = await res.json();
        setAssets(data.sort((a, b) => a.asset_id.localeCompare(b.asset_id)));
      } else {
        alert("An error occurred while loading assets.");
      }

      res = await apiRequest(`/brassica/offering/${props.params.id}`, {
        method: "get",
      });

      if (res.status === 200) {
        const data = await res.json();
        setOffering(data);
      } else {
        alert("An error occurred while loading the offering.");
      }

      setIsLoadingAssets(false);
    }

    if (assets.length === 0) {
      fetchData();
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    setIsSaving(true);

    const res = await apiRequest("/brassica/offering-series", {
      method: "post",

      body: JSON.stringify({
        offering_id: props.params.id,
        asset_id: attributes.asset_id,
      })
    });

    if (res.status === 200) {
      setLocation(`/brassica-offerings/${props.params.id}/assets`);
    } else {
      alert("An error occurred while associating the asset.");
    }

    setIsSaving(false);
  };

  if (isLoadingAssets) {
    return <Spinner message="Loading assets…" />;
  }

  if (isSaving) {
    return <Spinner message="Associating asset…" />;
  }

  return <form ref={formRef} onSubmit={handleSubmit}>
    <div className="sm:flex sm:items-center mb-6">
      <div className="sm:flex-auto">
        <h1 className="text-base font-semibold leading-6 text-gray-900">Brassica Offering: {offering.attributes.title}</h1>
        <p className="mt-2 text-sm text-gray-700">
          Associate a JKBX asset with this offering.
        </p>
      </div>
      <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none flex gap-4">
        <Link
          href={`/brassica-offerings/${props.params.id}/assets`}
          className="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
        >
          Back
        </Link>
      </div>
    </div>
    <div className="mb-6">
      <label htmlFor="asset_id" className="block text-sm font-medium leading-6 text-gray-900">
        JKBX Asset
      </label>
      <div className="mt-2">
        <select
          id="asset_id"
          value={attributes.asset_id}
          onInput={e => setAttributes({ ...attributes, asset_id: e.target.value })}
          className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
          required
        >
          {assets.map(asset => <option key={asset.asset_id} value={asset.asset_id}>{asset.asset_id} ({asset.song_title}{asset.rights_types && ` / ${asset.rights_types.join(', ')}`})</option>)}
        </select>
      </div>
    </div>
    <button
      type="submit"
      className="block rounded-md bg-blue-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
    >
      Associate Asset
    </button>
  </form>;
};
