import { useState, useRef } from 'react';
import useRequest from '../hooks/useRequest';
import Spinner from '../components/Spinner';
import Notice from '../components/Notice';
import * as styles from "./UploadTranscript.tailwind";

export default function UploadTranscript() {
    const fileInput = useRef(null);
    const [isUploading, setIsUploading] = useState(false);
    const [isPolling, setIsPolling] = useState(false);
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
            setIsPolling(true);

            const submitResponse = await apiRequest(`/file/${fileName}/tickets?number_of_tickets=20`, {
                method: "post"
            });

            if (submitResponse && !submitResponse.ok) {
                throw new Error('Ticket generation failed');
            }

            const submitedResponseJson = await submitResponse.json();
            console.log(submitedResponseJson);


            const pollTickets = async (fileName) => {
                let response = null;
                let count = 0;

                while (!response && count < 24) {
                    const res = await apiRequest(`/file/${fileName}/tickets?generation_datetime=${submitedResponseJson.ticket_generation_datetime}`, {
                        method: "get",
                    });

                    if (res.status === 200) {
                        let resJson = await res.json();
                        console.log(resJson);
                        if (resJson.tickets && resJson.tickets.length > 0) {
                            setIsPolling(false);
                            setTicketsResponse(resJson);
                            response = true;
                        } else {
                            await new Promise(resolve => setTimeout(resolve, 5000)); // Wait for 5 seconds before making the next request
                            count++;
                        }
                    } else {
                        await new Promise(resolve => setTimeout(resolve, 5000)); // Wait for 5 seconds before making the next request
                        count++;
                    }
                }

                if (!response) {
                    setIsPolling(false);
                    alert("Ticket generation timed out.");
                }
            };

            pollTickets(fileName);
        } catch (error) {
            setIsPolling(false);
            alert(error.message || "An error occurred while generating your tickets.");
        }
    };

    const saveTicket = async (fileName, subject, body, estimationPoints) => {

    };

    const uploadButton = (
        <label
            htmlFor="upload"
            className={styles.uploadButton_tw}
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

    return (
        response ? (
            <div className={styles.transcriptContainer_tw}>
                <Notice>Your transcript has been uploaded!</Notice>
                <BucketTable response={response} />
                <FileTable
                    generateTickets={generateTickets}
                    response={response}
                    ticketsResponse={ticketsResponse}
                    isPolling={isPolling}
                    isButtonOptionA={ticketsResponse} // if true, buttonOptionA is rendered, else buttonOptionB
                />
                {uploadButton}
                {ticketsResponse && <TicketTable ticketsResponse={ticketsResponse}/>}
            </div>
        ) : (
            <div className={styles.transcriptContainer_tw}>
                <Notice>
                    <p>Please note that currently only .txt files are supported</p>
                </Notice>
                {uploadButton}
            </div>
        )
    );
};

const BucketTable = ({ response }) => (
    <table className={styles.bucketTableContainer_tw}>
        <thead>
            <tr>
                <th scope="col" className={styles.tableHeader_tw}>Bucket</th>
            </tr>
        </thead>
        <tbody className={styles.tableBodyContainer_tw}>
            <tr>
                <td className="py-4 text-sm text-gray-500">{response.bucket}</td>
            </tr>
        </tbody>
    </table>
);

const FileTable = ({ generateTickets, response, ticketsResponse, isPolling, isButtonOptionA = true }) => {
    const buttonOptionA = (name) => (
        <td className="py-4 text-sm text-gray-500">
            <button
                className={styles.generateTicketsButton_tw}
                onClick={() => generateTickets(name)}
            >
                <span>Generate Tickets</span>
            </button>
        </td>
    );

    const buttonOptionB = (name) => (
        <td>
            <button
                className={styles.regenerateTicketsButton_tw}
                onClick={() => generateTickets(name)}
            >
                {isPolling ? (
                    <span className="flex items-center gap-x-2">
                        <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path
                                className="opacity-75"
                                fill="currentColor"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l1.414-1.414C2.56 15.544 1.5 13.88 1.5 12H6zm10-5.291A7.962 7.962 0 0120 12h4c0-6.627-5.373-12-12-12v4c3.042 0 5.824 1.135 7.938 3l-1.414 1.414z"
                            ></path>
                        </svg>
                        <p>Generating Tickets</p>
                    </span>
                    ) : <span>{ticketsResponse ? "Regenerate Tickets" : "Generate Tickets"}</span>
                }
            </button>
        </td>
    );

    return (
        <table className={styles.fileTableContainer_tw}>
            <caption className="text-left text-white font-semibold pb-3">File</caption>
            <thead>
                <tr>
                    <th scope="col" className={styles.tableHeader_tw}>Size</th>
                    <th scope="col" className={styles.tableHeader_tw}>File Name and URL</th>
                </tr>
            </thead>
            <tbody className={styles.tableBodyContainer_tw}>
                {Object.entries(response.files).map(([index, { name, url, size }]) => (
                    <tr key={index}>
                        <td className="py-3 text-sm text-white pr-3">{size + " KB"}</td>
                        <td className="py-3 text-sm text-gray-500">
                            <p className="font-medium">{name}</p>
                            <a
                                className={styles.fileTableUrl_tw}
                                href={url}
                                target="_blank"
                            >
                                {url}
                            </a>
                        </td>
                        {isButtonOptionA ? buttonOptionA(name) : buttonOptionB(name)}
                    </tr>
                ))}
            </tbody>
        </table>
    );
};

const TicketTable = ({ ticketsResponse}) => {
    const saveTicketButton = (subject, body, estimationPoints) => (
        <tr key={subject}>
            <td className="py-2 text-sm text-white pr-3 w-[25%]">{subject}</td>
            <td className="py-2 text-sm text-gray-500 pr-3 w-[55%]">{body}</td>
            <td className="py-2 text-sm text-gray-500 pr-3 text-center">{estimationPoints}</td>
            <td className="w-[10%]">
                <button
                    className={styles.saveTicketButton_tw}
                    onClick={() => saveTicket({ subject, body, estimationPoints })}
                >
                    Save Ticket
                </button>
            </td>
        </tr>
    );

    return (
        <table className={styles.ticketsTableContainer_tw}>
            <caption className="text-left text-white font-semibold pb-3">Tickets</caption>
            <thead>
                <tr>
                    <th scope="col" className={styles.tableHeader_tw}>Subject</th>
                    <th scope="col" className={styles.tableHeader_tw}>Description</th>
                    <th scope="col" className={[styles.tableHeader_tw, "text-center"].join(" ")}>Story Points</th>
                </tr>
            </thead>
            <tbody className={styles.tableBodyContainer_tw}>
                {ticketsResponse && ticketsResponse.tickets && Object.entries(ticketsResponse.tickets).map(
                    ([key, { subject, body, estimationpoints }]) => saveTicketButton(subject, body, estimationpoints)
                )}
            </tbody>
        </table>
    )
};