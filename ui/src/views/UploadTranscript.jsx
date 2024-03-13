import { useState, useRef, useContext } from 'react';
import useRequest from '../hooks/useRequest';
import Spinner from '../components/Spinner';
import Notice from '../components/Notice';
import TicketTable from '../components/tables/TicketsTable';
import UploadedFilesTable from '../components/tables/UploadedFilesTable';
import * as styles from "./UploadTranscript.tailwind";
import { UploadTranscriptContext } from '../context/UploadTranscriptContext';

export default function UploadTranscript() {
    const fileInput = useRef(null);
    const [isUploading, setIsUploading] = useState(false);
    const [isPolling, setIsPolling] = useState(false);
    const { ticketsResponse, setTicketsResponse, uploadResponse, setUploadResponse } = useContext(UploadTranscriptContext);
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
                const apiUploadResponse = await apiRequest('/upload', {
                    method: "post",
                    body: formData,
                });

                if (!apiUploadResponse.ok) {
                    throw new Error('Upload failed');
                }

                setIsUploading(false);
                setUploadResponse(await apiUploadResponse.json());
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
                setUploadResponse(null);
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
            <span>{uploadResponse ? "Upload another transcript" : "Upload transcript"}</span>
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
        uploadResponse ? (
            <div className={styles.transcriptContainer_tw}>
                <Notice>Your transcript has been uploaded!</Notice>
                <UploadedFilesTable
                    generateTickets={generateTickets}
                    response={uploadResponse}
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
