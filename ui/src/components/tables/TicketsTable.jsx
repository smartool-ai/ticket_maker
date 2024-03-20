import { useContext, useState } from 'react';
import ButtonSpinner from '../ButtonSpinner';
import { UploadTranscriptContext } from '../../context/UploadTranscriptContext';
import * as styles from './TicketsTable.tailwind';
import { strCombine, twId } from '../../utils/tailwindUtils';

export default function TicketTable({ saveTickets, isPolling }) {
	const { ticketsResponse, setTicketsResponse } = useContext(UploadTranscriptContext);
	const [showEditInput, setShowEditInput] = useState(false);
	const [editItemID, setEditItemID] = useState(false);

	const handleEditItem = (key) => {
		setShowEditInput(previous => !previous);
		setEditItemID(key);
	};

	const handleUpdateItem = (key, subjectValue, bodyValue, pointsValue, platformValue) => {
		const updatedItem = {
			subject: subjectValue,
			body: bodyValue,
			estimationpoints: pointsValue,
			// platform: platformValue,
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

		return (
			<tr key={key}>
				<td className={strCombine(styles.tableRow_tw, "text-white w-[20%]")}>
					{showEditInput && key === editItemID // check key and editItemId to only target the item clicked
						? <textarea required className={styles.tableRowTextArea_tw} onChange={(e) => setSubjectValue(e.target.value)} value={subjectValue} />
						: subjectValue
					}
				</td>
				<td className={strCombine(styles.tableRow_tw, "text-gray-500 w-[45%]")}>
					{showEditInput && key === editItemID
						? <textarea required type="text" className={styles.tableRowTextArea_tw} onChange={(e) => setBodyValue(e.target.value)} value={bodyValue} />
						: bodyValue
					}
				</td>
				<td className={strCombine(styles.tableRow_tw, "text-gray-500 text-center w-[6%]")}>
					{showEditInput && key === editItemID
						? <input required className={styles.tableRowInput_tw} onChange={(e) => setPointsValue(e.target.value)} value={pointsValue} />
						: pointsValue
					}
				</td>
				<td className={styles.tableDataSelect_tw}>
					<select id={key} className={styles.tableRowSelect_tw} onChange={(e) => setPlatformValue(e.target.value)} value={platformValue} >
						<option value="">Select an option</option>
						<option value="JIRA">Jira</option>
						<option value="SHORTCUT">Shortcut</option>
						<option value="ASANA">Asana</option>
					</select>
				</td>
				<td className={styles.tableDataButtons_tw}>
					<button
						id={`button${key}`}
						className={styles.button_tw}
						onClick={() => saveTickets(key, subject, body, estimationPoints)}
					>
						Create Ticket
					</button>
					<button
						className={strCombine("mt-2", styles.button_tw)}
						onClick={
							showEditInput
								? () => handleUpdateItem(key, subjectValue, bodyValue, pointsValue, platformValue)
								: () => handleEditItem(key)
						}
					>
						{showEditInput && key === editItemID ? "Save" : "Edit"}
					</button>
				</td>
			</tr>
		)
	};

	return (
		<table className={styles.table_tw}>
			<caption className={styles.tableCaption_tw}>Tickets</caption>
			{isPolling ? (
				<caption className={styles.tableCaptionLoading_tw}>
					<ButtonSpinner />
					Loading tickets...
				</caption>
			) : (
				<>
					<thead>
						<tr>
							<th scope="col" className={twId("left", styles.tableHeader_tw)}>Subject</th>
							<th scope="col" className={twId("left", styles.tableHeader_tw)}>Description</th>
							<th scope="col" className={twId("center", styles.tableHeader_tw)}>Story Points</th>
							<th scope="col" className={twId("center", styles.tableHeader_tw)}>Platform</th>
							<th scope="col" className={twId("center", styles.tableHeader_tw)}>Actions</th>
						</tr>
					</thead>
					<tbody className={styles.tableBody_tw}>
						{ticketsResponse && ticketsResponse.tickets && ticketsResponse.tickets.map(
							({subject, body, estimationpoints}, key) => ticketRowItem(key, subject, body, estimationpoints)
						)}
					</tbody>
				</>
			)}
		</table>
	);
};
