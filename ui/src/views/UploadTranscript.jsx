import { useState, useRef } from 'react';
import useRequest from '../hooks/useRequest';
import Spinner from '../components/Spinner';
import Notice from '../components/Notice';
import ButtonSpinner from '../components/ButtonSpinner';
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

    const saveTickets = async (key, subject, body, estimationPoints) => {
        const ticketParams = {"name": subject, "description": body, "estimate": estimationPoints}
        const submitResponse = await apiRequest(`/ticket?platform=${document.getElementById(key).value}`, {
            method: "post",
            body: ticketParams
        });

        if (submitResponse.status == 200) {
            document.getElementById(`button${key}`).innerHTML = "Ticket Uploaded";
        } else {
            alert(await submitResponse.text() || "An error occurred while saving your tickets.");
            console.log(await submitResponse.text() || "An error occurred while saving your tickets.");
        }
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
                />
                {uploadButton}
                {ticketsResponse && <TicketTable saveTickets={saveTickets} ticketsResponse={ticketsResponse} isPolling={isPolling} />}
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

const FileTable = ({ generateTickets, response, ticketsResponse, isPolling }) => {
    const generateTicketsButton = (name) => (
        <td>
            <button
                className={styles.generateTicketsButton_tw}
                onClick={() => generateTickets(name)}
            >
                {isPolling ? (
                    <span className="flex items-center gap-x-2">
                        <ButtonSpinner />
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
                        {generateTicketsButton(name)}
                    </tr>
                ))}
            </tbody>
        </table>
    );
};

const TicketTable = ({ saveTickets, ticketsResponse, isPolling }) => {
    const ticketRowItem = (key, subject, body, estimationPoints) => (
        <tr key={key}>
            <td className="py-3 text-sm text-white pr-3 w-[20%]">{subject}</td>
            <td className="py-3 text-sm text-gray-500 pr-3 w-[40%]">{body}</td>
            <td className="py-3 text-sm text-gray-500 pr-3 text-center">{estimationPoints}</td>
            <td className="w-[20%] text-center">
                <select id={key}>
                    <option value="">Select an option</option>
                    <option value="JIRA">Jira</option>
                    <option value="SHORTCUT">Shortcut</option>
                    <option value="ASANA">Asana</option>
                </select>
            </td>
            <td className="w-[10%]">
                <button
                    id={`button${key}`}
                    className={styles.saveTicketButton_tw}
                    onClick={() => saveTickets(key, subject, body, estimationPoints)}
                >
                    Upload Ticket
                </button>
            </td>
        </tr>
    );

    return (
        <table className={styles.ticketsTableContainer_tw}>
            <caption className="text-left text-white font-semibold pb-3">Tickets</caption>
            {isPolling ? (
                <caption className="p-10 flex justify-center items-center gap-x-2 text-white">
                    <ButtonSpinner />
                    Loading tickets...
                </caption>
            ) : (
                <>
                    <thead>
                        <tr>
                            <th scope="col" className={styles.tableHeader_tw}>Subject</th>
                            <th scope="col" className={styles.tableHeader_tw}>Description</th>
                            <th scope="col" className={[styles.tableHeader_tw, "text-center"].join(" ")}>Story Points</th>
                            <th scope="col" className={[styles.tableHeader_tw, "text-center"].join(" ")}>Upload To</th>
                        </tr>
                    </thead>
                    <tbody className={styles.tableBodyContainer_tw}>
                        {ticketsResponse && ticketsResponse.tickets && Object.entries(ticketsResponse.tickets).map(
                            ([key, { subject, body, estimationpoints }]) => ticketRowItem(key, subject, body, estimationpoints)
                        )}
                    </tbody>
                </>
            )}
        </table>
    );
};