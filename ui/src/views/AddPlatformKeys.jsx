import React, { useState } from 'react';
import useRequest from '../hooks/useRequest';

const AddPlatformKeys = () => {
  const [platform, setPlatform] = useState('');
  const [email, setEmail] = useState(null);
  const [server, setServer] = useState(null);
  const [apiKey, setApiKey] = useState(null);
  const [projectId, setProjectId] = useState(null);
  const [personalAccessToken, setPat] = useState(null);
  const [workspaceId, setWorkspaceId] = useState(null);
  const apiRequest = useRequest();

  const handlePlatformChange = (event) => {
    setPlatform(event.target.value);
  };

  const handleEmailChange = (value) => {
    setEmail(value);
  };

  const handleServerChange = (value) => {
    setServer(value);
  };

  const handleApiKeyChange = (value) => {
    setApiKey(value);
  };

  const handleProjectIdChange = (value) => {
    setProjectId(value);
  };

  const handlePatChange = (value) => {
    setPat(value);
  };

  const handleWorkspaceIdChange = (value) => {
    setWorkspaceId(value);
  };

  const save = async (email, server, apiKey, personalAccessToken, projectId, workspaceId) => {
    const reqBody = {
      "email": email,
      "server": server,
      "api_key": apiKey,
      "personal_access_token": personalAccessToken,
      "project_id": projectId,
      "workspace_id": workspaceId
    }
    console.log('Platform:', platform);
    const saveResponse = await apiRequest(`/user-metadata/link?platform=${platform.toUpperCase()}`, {
      method: "put",
      body: reqBody,
    });

    if (saveResponse.status === 200) {
      console.log('Platform keys saved');
      document.getElementById('saveButton').disabled = true;
      document.getElementById('saveButton').innerHTML = 'Saved';
    } else {
      alert('Error saving platform keys')
      console.log('Error saving platform keys');
    }
  };

  const renderFormFields = (email, server, apiKey, personalAccessToken, projectId, workspaceId) => {
    if (platform === 'Jira') {
      return (
        <div className="flex flex-col gap-y-3">
          <label htmlFor="email" className="block text-sm font-medium leading-6 text-white">
            Jira Email
          </label>
          <input
            id="email"
            type="email"
            value={email} onChange={e => handleEmailChange(e.target.value)}
            className="block max-w-sm w-full rounded-md border-0 px-3 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
            placeholder="you@example.com"
          />
          <label htmlFor="server" className="block text-sm font-medium leading-6 text-white">
            Jira Server Adress
          </label>
          <input
            id="server"
            type="server"
            value={server} onChange={e => handleServerChange(e.target.value)}
            className="block max-w-sm w-full rounded-md border-0 px-3 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
            placeholder="https://yourcompany.atlassian.net"
          />
          <label htmlFor="apiKey" className="block text-sm font-medium leading-6 text-white">
            Jira API Key
          </label>
          <input
            id="apiKey"
            type="apiKey"
            value={apiKey} onChange={e => handleApiKeyChange(e.target.value)}
            className="block max-w-sm w-full rounded-md border-0 px-3 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
            placeholder="your-api-key"
          />
        </div>
      );
    } else if (platform === 'Asana') {
      return (
        <div>
          <label htmlFor="personalAccessToken" className="block text-sm font-medium leading-6 text-white">
            Asana Personal Access Token
          </label>
          <input
            id="personalAccessToken"
            type="personalAccessToken"
            value={personalAccessToken} onChange={e => handlePatChange(e.target.value)}
            className="block max-w-sm w-full rounded-md border-0 px-3 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
            placeholder="your-personal-access-token"
          />
          <label htmlFor="workspaceId" className="block text-sm font-medium leading-6 text-white">
            Asana Workspace Id
          </label>
          <input
            id="workspaceId"
            type="workspaceId"
            value={workspaceId} onChange={e => handleWorkspaceIdChange(e.target.value)}
            className="block max-w-sm w-full rounded-md border-0 px-3 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
            placeholder="your-workspace-id"
          />
          <label htmlFor="projectId" className="block text-sm font-medium leading-6 text-white">
            Asana Project ID
          </label>
          <input
            id="projectId"
            type="projectId"
            value={projectId} onChange={e => handleProjectIdChange(e.target.value)}
            className="block max-w-sm w-full rounded-md border-0 px-3 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
            placeholder="your-project-id"
          />
        </div>
      );
    } else if (platform === 'Shortcut') {
      return (
        <div>
          <label htmlFor="apiKey" className="block text-sm font-medium leading-6 text-white">
            Shortcut API Key
          </label>
          <input
            id="apiKey"
            type="apiKey"
            value={apiKey} onChange={e => handleApiKeyChange(e.target.value)}
            className="block max-w-sm w-full rounded-md border-0 px-3 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
            placeholder="your-api-key"
          />
          <label htmlFor="projectId" className="block text-sm font-medium leading-6 text-white">
            Shortcut Project ID
          </label>
          <input
            id="projectId"
            type="projectId"
            value={projectId} onChange={e => handleProjectIdChange(e.target.value)}
            className="block max-w-sm w-full rounded-md border-0 px-3 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
            placeholder="your-project-id"
          />
        </div>
      );
    } else {
      return null;
    }
  };

  const saveButton = (email, server, apiKey, personalAccessToken, projectId, workspaceId) => {
    return (
      <div>
        <button
          id="saveButton"
          type="button"
          onClick={() => save(email, server, apiKey, personalAccessToken, projectId, workspaceId)}
          className="rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-[#4654A3] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
        >
          Save
        </button>
      </div>
    )
  };

  return (
    <div>
      <h1>
        <label htmlFor="apiKey" className="block text-sm font-medium leading-6 text-white">
          Add Platform Keys
        </label>
      </h1>

      <label htmlFor="platform" className="block text-sm font-medium leading-6 text-white">Select Platform:</label>
      <select id="platform" name="platform" value={platform} onChange={handlePlatformChange}>
        <option value="">Select</option>
        <option value="Jira">Jira</option>
        <option value="Asana">Asana</option>
        <option value="Shortcut">Shortcut</option>
      </select>

      {renderFormFields(email, server, apiKey, personalAccessToken, projectId, workspaceId)}

      {saveButton(email, server, apiKey, personalAccessToken, projectId, workspaceId)}
    </div>
  );
};

export default AddPlatformKeys;
