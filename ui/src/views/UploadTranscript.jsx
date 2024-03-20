import { useState, useRef, useContext } from 'react';
import useRequest from '../hooks/useRequest';
import Spinner from '../components/Spinner';
import Toast from '../components/Toast';
import TicketTable from '../components/tables/TicketsTable';
import UploadedFilesTable from '../components/tables/UploadedFilesTable';
import * as styles from "./UploadTranscript.tailwind";
import { UploadTranscriptContext } from '../context/UploadTranscriptContext';

export default function UploadTranscript() {
	const fileInput = useRef(null);
	const [isUploading, setIsUploading] = useState(false);
	const [isPolling, setIsPolling] = useState(false);
	const [toast, setToast] = useState({
		showToast: true,
		label: "Please note that currently only .txt files are supported.",
		type: "info"
	});
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
				setToast({
					type: "success",
					label: "Your transcript has been uploaded!",
					showToast: true,
				});
			} catch (error) {
				setIsUploading(false);
				setToast({
					type: "error",
					label: "An error occurred while uploading your file.",
					showToast: true,
				});
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
			setToast({
				type: "error",
				label: "An error occurred while uploading your file.",
				showToast: true,
			});
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
					setToast({
						type: "error",
						label: "Ticket generation timed out.",
						showToast: true,
					});
				}
			};

			pollTickets(fileName);
		} catch (error) {
			setIsPolling(false);
			setToast({
				type: "error",
				label: error.message || "An error occurred while generating your tickets.",
				showToast: true,
			});
		}
	};

	const saveTickets = async (key, subject, body, estimationPoints) => {
		const ticketParams = { "name": subject, "description": body, "estimate": estimationPoints }
		const submitResponse = await apiRequest(`/ticket?platform=${document.getElementById(key).value}`, {
			method: "post",
			body: ticketParams
		});

		if (submitResponse.status == 200) {
			document.getElementById(`button${key}`).innerHTML = "Ticket Uploaded";
		} else {
			setToast({
				type: "error",
				label: await submitResponse.text() || "An error occurred while saving your tickets.",
				showToast: true,
			});
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

	const handleClearAll = () => {
		setTicketsResponse(null);
		setUploadResponse(null);
	};

	const clearButton = (handleOnClick, buttonLabel) => (
		<button className={styles.uploadButton_tw} onClick={handleOnClick}>
			{buttonLabel}
		</button>
	);

	return (
		<>
			{toast.showToast && <Toast type={toast.type} label={toast.label} onClose={() => setToast(previous => ({ ...previous, showToast: false }))} />}
			{uploadResponse ? (
				<div className={styles.transcriptContainer_tw}>
					<UploadedFilesTable
						generateTickets={generateTickets}
						response={uploadResponse}
						ticketsResponse={ticketsResponse}
						isPolling={isPolling}
					/>
					<div className="flex gap-3">
						{uploadButton}
						{!ticketsResponse && uploadResponse && clearButton(() => setUploadResponse(null), "Clear uploaded files")}
						{ticketsResponse && clearButton(() => setTicketsResponse(null), "Clear generated tickets")}
						{ticketsResponse && clearButton(handleClearAll, "Clear All")}
					</div>
					{ticketsResponse && <TicketTable saveTickets={saveTickets} isPolling={isPolling} />}
				</div>
			) : (
				<div className={styles.transcriptContainer_tw}>
					<div className="text-gray-400 border-gray-900 border-4 rounded-md p-4">
						Drag and Drop here
					</div>
					{uploadButton}
				</div>
			)}
		</>
	);
};
