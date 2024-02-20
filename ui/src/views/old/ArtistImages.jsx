import { useState, useRef } from 'react';
import useRequest from '../../hooks/useRequest';
import Spinner from '../../components/Spinner';
import Notice from '../../components/Notice';

export default function ArtistImages() {
  const fileInput = useRef(null);
  const [isUploading, setIsUploading] = useState(false);
  const [response, setResponse] = useState(null);
  const apiRequest = useRequest();

  if (isUploading) {
    return <Spinner />;
  }

  const doUpload = async () => {
    const fileName = fileInput.current.files[0].name;

    const formData = new FormData();
    formData.append("upload", fileInput.current.files[0]);

    const uploadHandler = async () => {
      const uploadResponse = await apiRequest('/artist_image', {
        method: "post",
        body: formData,
      });

      setIsUploading(false);

      setResponse(await uploadResponse.json());
    };

    setIsUploading(true);

    const res = await apiRequest(`/artist_image/${fileName}`, {
      method: "get",
    });

    if (res.status === 200) {
      if (
        confirm(
          `An image with the name "${fileName}" already exists. Are you sure you want to overwrite it?`,
        )
      ) {
        uploadHandler();
      } else {
        setIsUploading(false);
        setResponse(null);
      }
    } else if (res.status === 404) {
      uploadHandler();
    } else {
      setIsUploading(false);
      alert("An error occurred while uploading your image.");
    }
  };

  const uploadButton = (
    <label
      htmlFor="upload"
      className="relative cursor-pointer flex w-full justify-center rounded-md bg-blue-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
    >
      <span>{response ? "Upload another image" : "Upload image"}</span>
      <input
        type="file"
        id="upload"
        name="upload"
        ref={fileInput}
        onChange={doUpload}
        className="sr-only"
      />
    </label>
  );

  return response ? (
    <div className="flex flex-col gap-6">
      <Notice>
        Your image has been uploaded!
      </Notice>

      <table className="w-full divide-y divide-gray-300">
        <thead>
          <tr>
            <th
              scope="col"
              className="py-3.5 text-left text-sm font-semibold text-gray-900"
            >
              Bucket
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          <tr>
            <td className="py-4 text-sm text-gray-500">
              {response.bucket}
            </td>
          </tr>
        </tbody>
      </table>

      <table className="w-full divide-y divide-gray-300">
        <thead>
          <tr>
            <th
              scope="col"
              colSpan="3"
              className="py-3.5 text-left text-sm font-semibold text-gray-900"
            >
              File
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {Object.entries(response.files).map(
            ([size, { name, url }]) => (
              <tr key={size}>
                <td className="py-4 text-sm text-gray-500 pr-3">
                  {size}
                </td>
                <td className="py-4 text-sm text-gray-500">
                  <p className="font-medium">{name}</p>
                  <a
                    className="text-blue-600 hover:text-blue-900 text-xs"
                    href={url}
                    target="_blank"
                  >
                    {url}
                  </a>
                </td>
              </tr>
            ),
          )}
        </tbody>
      </table>

      {uploadButton}
    </div>
  ) : (
    <div className="flex flex-col gap-6">
      <Notice>
        <p>Please make sure your image filename follows this format before uploading:</p>
        <p className="font-semibold">artist_name_xlarge.extension</p>
        <p>For example: ed_sheeran_xlarge.jpg</p>
      </Notice>

      {uploadButton}
    </div>
  )
};
