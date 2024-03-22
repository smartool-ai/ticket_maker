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
	const [generationDatetime, setGenerationDatetime] = useState(null);
	const [isUploading, setIsUploading] = useState(false);
	const [isExpanding, setIsExpanding] = useState(false);
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

	const uploadTranscriptFile = async () => {
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
			setGenerationDatetime(submitedResponseJson.ticket_generation_datetime);
			console.log(submitedResponseJson);


			const pollTickets = async (fileName) => {
				let response = null;
				let count = 0;

				while (!response && count < 24) {
					const res = await apiRequest(`/file/${fileName}/tickets?generation_datetime=${generationDatetime}`, {
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

	const expandTickets = async (id, subject, body, estimationPoints) => {
		setIsExpanding(true);
		const expandBody = { "name": subject, "description": body, "estimate": estimationPoints };
		const fileName = uploadResponse.files[0].name; // HARDCODED 0 assuming we can only upload one file at a time
		const expandResponse = await apiRequest(`/file/${fileName}/tickets/expand?generation_datetime=${generationDatetime}`, {
			method: "POST",
			body: expandBody,
		});
		
		if (expandResponse.status == 200) {
			const expandResponseJson = await expandResponse.json();
			const subTickets = await getSubTickets(id, expandResponseJson.sub_ticket_id);
			const consolidatedTickets = consolidateAllTickets(id, subTickets);
			setTicketsResponse({tickets: consolidatedTickets});
			setToast({
				type: "success",
				label: `Ticket: ${subject} has been successfully expanded!`,
				showToast: true,
			});
		} else {
			setToast({
				type: "error",
				label: await expandResponse.text() || "An error occurred while expanding your ticket.",
				showToast: true,
			});
		}
		setIsExpanding(false);
	};

	const getSubTickets = async (id, subTicketId) => {
		const getSubTicketResponse = await apiRequest(`/ticket/sub/${subTicketId}`, { method: "GET" });
		
		if (getSubTicketResponse.status == 200) {
			const subTicketResponseJson = await getSubTicketResponse.json();

			return subTicketResponseJson.tickets.map((ticket) => ({...ticket, subTicketOf: id}));
		} else {
			setToast({
				type: "error",
				label: await getSubTicketResponse.text() || "An error occurred while retrieving sub ticket.",
				showToast: true,
			});
		}
	};
	
	const consolidateAllTickets = (id, subTickets) => {
		const mainTicketIndex = ticketsResponse.tickets.findIndex(ticket => ticket.id === id);
		const sliceFirstHalf = ticketsResponse.tickets.slice(0, mainTicketIndex);
		
		// Add 'expanded' field to limit ticket expansion once
		const expandedTicket = {...ticketsResponse.tickets[mainTicketIndex], expanded: true};

		const sliceSecondHalf = ticketsResponse.tickets.slice(mainTicketIndex + 1);
		return [...sliceFirstHalf, expandedTicket, ...subTickets, ...sliceSecondHalf];
	};
	const saveTickets = async (id, subject, body, estimationPoints) => {
		const ticketParams = { "name": subject, "description": body, "estimate": estimationPoints };
		const submitResponse = await apiRequest(`/ticket?platform=${document.getElementById(id).value}`, {
			method: "post",
			body: ticketParams
		});

		if (submitResponse.status == 200) {
			document.getElementById(`button${id}`).innerHTML = "Ticket Uploaded";
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
				onChange={uploadTranscriptFile}
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
					{ticketsResponse && (
						<TicketTable
							expandTickets={expandTickets}
							saveTickets={saveTickets}
							isPolling={isPolling}
							setToast={setToast}
							isExpanding={isExpanding}
						/>
					)}
				</div>
			) : (
				<div className={styles.transcriptContainer_tw}>
					<div className="text-gray-400 border-gray-900 border-4 rounded-md p-4">
						Placeholder: Drag and Drop
					</div>
					{uploadButton}
				</div>
			)}
		</>
	);
}
