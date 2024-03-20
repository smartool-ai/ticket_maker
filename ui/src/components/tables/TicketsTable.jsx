import { useContext, useState } from 'react';
import ButtonSpinner from '../ButtonSpinner';
import { UploadTranscriptContext } from '../../context/UploadTranscriptContext';

export default function TicketTable({ saveTickets, isPolling }) {
	const { ticketsResponse, setTicketsResponse } = useContext(UploadTranscriptContext);
	const [showEditInput, setShowEditInput] = useState(false);
	const [editItemID, setEditItemID] = useState(false);

	const handleEditItem = (key, e) => {
		setShowEditInput(previous => !previous);
		setEditItemID(key);
	};

	const handleUpdateItem = (e, key, subjectValue, bodyValue, pointsValue, platformValue) => {
		const updatedItem = {
			subjectValue,
			bodyValue,
			pointsValue,
			platformValue,
		};
		const newTickets = [...ticketsResponse.tickets];
		newTickets[key] = updatedItem;
		setTicketsResponse(previous => ({...previous, tickets: [...newTickets]}));
		setShowEditInput(previous => !previous);
	};
	
	const ticketRowItem = (key, subject, body, estimationPoints) => {
		const [subjectValue, setSubjectValue] = useState(subject);
		const [bodyValue, setBodyValue] = useState(body);
		const [pointsValue, setPointsValue] = useState(estimationPoints);
		const [platformValue, setPlatformValue] = useState("");
		// THESE STATES BECOMES UNDEFINED AFTER IT UNMOUNTS

		return (
			<tr key={key}>
				<td className="py-3 text-sm text-white pr-3 w-[20%]">
					{showEditInput && key === editItemID // check key and editItemId to only target the item clicked
						? <textarea required className="h-fit w-full text-sm border bg-inherit" onChange={(e) => setSubjectValue(e.target.value)} value={subjectValue} />
						: subjectValue
					}
				</td>
				<td className="py-3 text-sm text-gray-500 pr-3 w-[45%]">
					{showEditInput && key === editItemID
						? <textarea required type="text" className="h-fit w-full text-sm border bg-inherit" onChange={(e) => setBodyValue(e.target.value)} value={bodyValue} />
						: bodyValue
					}
				</td>
				<td className="py-3 text-sm text-gray-500 pr-3 text-center w-[6%]">
					{showEditInput && key === editItemID
						? <input required className="h-fit w-[40px] text-sm border bg-inherit" onChange={(e) => setPointsValue(e.target.value)} value={pointsValue} />
						: pointsValue
					}
				</td>
				<td className="w-[11%] text-center">
					<select id={key} className="bg-inherit text-sm text-white rounded-md" onChange={(e) => setPlatformValue(e.target.value)} value={platformValue} >
						<option value="">Select an option</option>
						<option value="JIRA">Jira</option>
						<option value="SHORTCUT">Shortcut</option>
						<option value="ASANA">Asana</option>
					</select>
				</td>
				<td className="w-[8%] text-center">
					<button
						id={`button${key}`}
						className="w-full cursor-pointer rounded-md bg-blue-600 py-1 px-3 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-[#4654A3] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
						onClick={() => saveTickets(key, subject, body, estimationPoints)}
					>
						Create Ticket
					</button>
					<button
						className="mt-2 w-full cursor-pointer rounded-md bg-blue-600 py-1 px-3 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-[#4654A3] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
						onClick={showEditInput ? (e) => handleUpdateItem(e, key, subjectValue, bodyValue, pointsValue, platformValue) : (e) => handleEditItem(key, e)}
					>
						{showEditInput && key === editItemID ? "Save" : "Edit"}
					</button>
				</td>
			</tr>
		)
	};

	return (
		<table className="mt-6 w-full divide-y divide-gray-300">
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
							<th scope="col" className="py-3 text-left text-sm font-semibold text-white">Subject</th>
							<th scope="col" className="py-3 text-left text-sm font-semibold text-white">Description</th>
							<th scope="col" className="py-3 text-sm font-semibold text-white text-center">Story Points</th>
							<th scope="col" className="py-3 text-sm font-semibold text-white text-center">Platform</th>
							<th scope="col" className="py-3 text-sm font-semibold text-white text-center">Actions</th>
						</tr>
					</thead>
					<tbody className="divide-y divide-gray-200">
						{ticketsResponse && ticketsResponse.tickets && ticketsResponse.tickets.map(
							({subject, body, estimationpoints}, key) => ticketRowItem(key, subject, body, estimationpoints)
						)}
					</tbody>
				</>
			)}
		</table>
	);
};