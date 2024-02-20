import { useState, useRef, useEffect } from "react";
import useRequest from '../../hooks/useRequest';
import Spinner from '../../components/Spinner';
import { useLocation } from "wouter";
import { Link } from "wouter";
import dayjs from 'dayjs';

export default function CreateBrassicaOffering() {
  const apiRequest = useRequest();

  const formRef = useRef(null);

  const [attributes, setAttributes] = useState({
    "issuer_id": "",
    "agreement_template_id": "",
    "description": "",
    "title": "",
    "targetStartDate": dayjs().format('YYYY-MM-DD'),
    "targetTerminationDate": dayjs().add(6, 'month').format('YYYY-MM-DD'),
    "targetRaiseAmount": 1000000000,
    "offeringType": "reg-a-t2",
  });

  const [isSaving, setIsSaving] = useState(false);

  const [isLoadingIssuers, setIsLoadingIssuers] = useState(true);
  const [issuers, setIssuers] = useState([]);
  const [isLoadingAgreementTemplates, setIsLoadingAgreementTemplates] = useState(true);
  const [agreementTemplates, setAgreementTemplates] = useState([]);

  const [, setLocation] = useLocation();

  useEffect(() => {
    async function fetchData() {
      setIsLoadingIssuers(true);

      const res = await apiRequest("/brassica/issuers", {
        method: "get",
      });

      if (res.status === 200) {
        const data = await res.json();
        setIssuers(data.sort((a, b) => a.attributes.name.localeCompare(b.attributes.name)));
      } else {
        alert("An error occurred while loading issuers.");
      }

      setIsLoadingIssuers(false);
    }

    if (issuers.length === 0) {
      fetchData();
    }
  }, []);

  useEffect(() => {
    async function fetchData() {
      setIsLoadingAgreementTemplates(true);

      const res = await apiRequest("/brassica/agreement-templates", {
        method: "get",
      });

      if (res.status === 200) {
        const data = await res.json();
        setAgreementTemplates(data.sort((a, b) => a.attributes.name.localeCompare(b.attributes.name)));
      } else {
        alert("An error occurred while loading agreement templates.");
      }

      setIsLoadingAgreementTemplates(false);
    }

    if (agreementTemplates.length === 0) {
      fetchData();
    }
  }, []);

  useEffect(() => {
    if (!attributes.issuer_id && issuers.length > 0) {
      setAttributes({ ...attributes, issuer_id: issuers[0].id });
    }
  }, [issuers, attributes]);

  useEffect(() => {
    if (!attributes.agreement_template_id && agreementTemplates.length > 0) {
      setAttributes({ ...attributes, agreement_template_id: agreementTemplates[0].id });
    }
  }, [agreementTemplates, attributes]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    setIsSaving(true);

    const res = await apiRequest("/brassica/offerings", {
      method: "post",

      body: JSON.stringify({
        issuer_id: attributes.issuer_id,
        agreement_template_id: attributes.agreement_template_id,
        title: attributes.title,
        description: attributes.description,
        targetStartDate: attributes.targetStartDate,
        targetTerminationDate: attributes.targetTerminationDate,
        targetRaiseAmount: attributes.targetRaiseAmount,
        offeringType: attributes.offeringType,
      })
    });

    if (res.status === 200) {
      setLocation("/brassica-offerings");
    } else {
      alert("An error occurred while creating the offering.");
    }

    setIsSaving(false);
  };

  if (isLoadingIssuers) {
    return <Spinner message="Loading issuers…" />;
  }

  if (isLoadingAgreementTemplates) {
    return <Spinner message="Loading agreement templates…" />;
  }

  if (isSaving) {
    return <Spinner message="Creating offering…" />;
  }

  return <form ref={formRef} onSubmit={handleSubmit}>
    <div className="sm:flex sm:items-center mb-6">
      <div className="sm:flex-auto">
        <h1 className="text-base font-semibold leading-6 text-gray-900">Create Brassica Offerings</h1>
        <p className="mt-2 text-sm text-gray-700">
          Create or manage an existing offering to add or remove assets.
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
        <label htmlFor="issuer_id" className="block text-sm font-medium leading-6 text-gray-900">
          Issuer
        </label>
        <div className="mt-2">
          <select
            id="issuer_id"
            value={attributes.issuer_id}
            onInput={e => setAttributes({ ...attributes, issuer_id: e.target.value })}
            className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
            required
          >
            {issuers.map(issuer => <option key={issuer.id} value={issuer.id}>{issuer.attributes.name}</option>)}
          </select>
        </div>
      </div>
      <div>
        <label htmlFor="agreement_template_id" className="block text-sm font-medium leading-6 text-gray-900">
          Purchase Agreement
        </label>
        <div className="mt-2">
          <select
            id="agreement_template_id"
            value={attributes.agreement_template_id}
            onInput={e => setAttributes({ ...attributes, agreement_template_id: e.target.value })}
            className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
            required
          >
            {agreementTemplates.map(agreementTemplate => <option key={agreementTemplate.id} value={agreementTemplate.id}>{agreementTemplate.attributes.name}</option>)}
          </select>
        </div>
      </div>
      <div>
        <label htmlFor="title" className="block text-sm font-medium leading-6 text-gray-900">
          Title
        </label>
        <div className="mt-2">
          <input
            id="title"
            type="text"
            value={attributes.title}
            onInput={e => setAttributes({ ...attributes, title: e.target.value })}
            placeholder="JKBX HITS VOL1"
            className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
            required
          />
        </div>
      </div>
      <div>
        <label htmlFor="description" className="block text-sm font-medium leading-6 text-gray-900">
          Description
        </label>
        <div className="mt-2">
          <input
            id="description"
            type="text"
            value={attributes.description}
            onInput={e => setAttributes({ ...attributes, description: e.target.value })}
            placeholder="VOL. 1"
            className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
            required
          />
        </div>
      </div>
      <div>
        <label htmlFor="target_start_date" className="block text-sm font-medium leading-6 text-gray-900">
          Target Start Date
        </label>
        <div className="mt-2">
          <input
            id="target_start_date"
            type="date"
            value={attributes.targetStartDate}
            onInput={e => setAttributes({ ...attributes, targetStartDate: e.target.value })}
            className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
            required
          />
        </div>
      </div>
      <div>
        <label htmlFor="target_termination_date" className="block text-sm font-medium leading-6 text-gray-900">
          Target Termination Date
        </label>
        <div className="mt-2">
          <input
            id="target_termination_date"
            type="date"
            value={attributes.targetTerminationDate}
            onInput={e => setAttributes({ ...attributes, targetTerminationDate: e.target.value })}
            className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
            required
          />
        </div>
      </div>
      <div>
        <label htmlFor="target_raise_amount" className="block text-sm font-medium leading-6 text-gray-900">
          Target Raise Amount
        </label>
        <div className="mt-2">
          <input
            id="target_raise_amount"
            type="number"
            value={attributes.targetRaiseAmount}
            onInput={e => setAttributes({ ...attributes, targetRaiseAmount: e.target.value })}
            placeholder="1000000000"
            className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
            required
          />
        </div>
      </div>
      <div>
        <label htmlFor="offering_type" className="block text-sm font-medium leading-6 text-gray-900">
          Offering Type
        </label>
        <div className="mt-2">
          <select
            id="offering_type"
            value={attributes.offeringType}
            onInput={e => setAttributes({ ...attributes, offeringType: e.target.value })}
            className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
            required
          >
            <option value="reg-a-t1">reg-a-t1</option>
            <option value="reg-a-t2">reg-a-t2</option>
            <option value="reg-cf-4a6">reg-cf-4a6</option>
            <option value="reg-d-506b">reg-d-506b</option>
            <option value="reg-d-506c">reg-d-506c</option>
          </select>
        </div>
      </div>
    </div>
    <button
      type="submit"
      className="block rounded-md bg-blue-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
    >
      Create Offering
    </button>
  </form>;
};
