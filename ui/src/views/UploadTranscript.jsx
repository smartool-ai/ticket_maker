import { useState, useRef } from 'react';
import useRequest from '../hooks/useRequest';
import Spinner from '../components/Spinner';
import Notice from '../components/Notice';

export default function UploadTranscript() {
    const fileInput = useRef(null);
    const [isUploading, setIsUploading] = useState(false);
    const [response, setResponse] = useState(null);
    const [ticketsResponse, setTicketsResponse] = useState(null);
    const apiRequest = useRequest();

    if (isUploading) {
        return <Spinner />;
    }

    const doUpload = async () => {
        const fileName = fileInput.current.files[0].name;

        const formData = new FormData();
        formData.append("file", fileInput.current.files[0]);

        const uploadHandler = async () => {
            try {
                const uploadResponse = await apiRequest('/upload', {
                    method: "post",
                    body: formData,
                });

                if (!uploadResponse.ok) {
                    throw new Error('Upload failed');
                }

                setIsUploading(false);
                setResponse(await uploadResponse.json());
            } catch (error) {
                setIsUploading(false);
                alert(error.message || "An error occurred while uploading your file.");
            }
        };

        setIsUploading(true);

        const res = await apiRequest(`/file/${fileName}`, {
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

    const generateTickets = async (fileName) => {
        try {
            setIsUploading(true);

            const submitResponse = await apiRequest(`/file/${fileName}/tickets`, {
                method: "get"
            });

            if (submitResponse && !submitResponse.ok) {
                throw new Error('Ticket generation failed');
            }

            setIsUploading(false);
            setTicketsResponse(await submitResponse.json());
        } catch (error) {
            setIsUploading(false);
            alert(error.message || "An error occurred while generating your tickets.");
        }
    };

    const uploadButton = (
        <label
            htmlFor="upload"
            className="relative cursor-pointer flex w-full justify-center rounded-md bg-blue-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
        >
            <span>{response ? "Upload another transcript" : "Upload transcript"}</span>
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

    return response ? ticketsResponse ? (
        <div className="flex flex-col gap-6">
            <Notice>
                Your transcript has been uploaded!
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
                    {Object.entries(response.files).map(([size, { name, url }]) => (
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
                            <td>
                                <button
                                    className="relative cursor-pointer flex w-full justify-center rounded-md bg-blue-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
                                    onClick={() => generateTickets({name})}
                                >
                                    <span>{ticketsResponse ? "Regenerate Tickets" : "Generate Tickets"}</span>

                                </button>
                            </td>
                        </tr>
                    ))}
                    {ticketsResponse && ticketsResponse.tickets && Object.entries(ticketsResponse.tickets).map(([key, { subject, body, estimationPoints }]) => (
                        <tr key={subject}>
                            <td className="py-4 text-sm text-black-500 pr-3">
                                {subject}
                            </td>
                            <td className="py-4 text-sm text-gray-500">
                                {body}
                            </td>
                            <td className="py-4 text-sm text-gray-500">
                                {estimationPoints}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {uploadButton}
        </div>
    ) : (
        <div className="flex flex-col gap-6">
            <Notice>
                Your transcript has been uploaded!
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
                    {Object.entries(response.files).map(([size, { name, url }]) => (
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
                            <td className="py-4 text-sm text-gray-500">
                                <button
                                    className="relative cursor-pointer flex w-full justify-center rounded-md bg-blue-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
                                    onClick={() => generateTickets(name)}
                                >
                                    <span>Generate Tickets</span>

                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {uploadButton}
        </div>
    ) : (
        <div className="flex flex-col gap-6">
            <Notice>
                <p>Please note that currently only .txt files are supported</p>
            </Notice>

            {uploadButton}
        </div>
    );
};
