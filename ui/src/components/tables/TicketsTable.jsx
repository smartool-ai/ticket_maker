import { useContext, useState } from 'react';
import ButtonSpinner from '../ButtonSpinner';
import { ArrowDownRightIcon } from '@heroicons/react/20/solid';
import { UploadTranscriptContext } from '../../context/UploadTranscriptContext';
import { strCombine, twConditional, twId } from '../../utils/tailwindUtils';
import * as styles from './TicketsTable.tailwind';

export default function TicketTable({ expandTickets, saveTickets, isPolling, setToast, isExpanding }) {
	const { ticketsResponse, setTicketsResponse } = useContext(UploadTranscriptContext);
	const [showEditInput, setShowEditInput] = useState(false);
	const [editItemID, setEditItemID] = useState(null);

	const handleEditItem = (id) => {
		setShowEditInput(previous => !previous);
		setEditItemID(id);
	};

	const handleExpandItem = (id, subject, body, estimationPoints) => {
		expandTickets(id, subject, body, estimationPoints);
		setEditItemID(id);
	};

	const handleUpdateItem = (id, subjectValue, bodyValue, pointsValue) => {
		const itemIndex = ticketsResponse.tickets.findIndex(ticket => ticket.id === id);
		const newTickets = [...ticketsResponse.tickets];
		
		const updatedItem = {
			id: id,
			subject: subjectValue,
			body: bodyValue,
			estimationpoints: pointsValue,
			subTicketOf: newTickets[itemIndex].subTicketOf,
			expanded: newTickets[itemIndex].expanded,
		};
		
		newTickets[itemIndex] = updatedItem;
		setTicketsResponse(previous => ({ ...previous, tickets: [...newTickets] }));
		setShowEditInput(previous => !previous);
		setToast({
			type: "success",
			label: `Your ticket has been updated.`,
			showToast: true,
		});
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
							(ticket) => (
								<TicketRowItem
									editItemID={editItemID}	
									showEditInput={showEditInput}
									handleEditItem={handleEditItem}
									handleUpdateItem={handleUpdateItem}
									key={ticket.id}
									ticket={ticket}
									saveTickets={saveTickets}
									isExpanding={isExpanding}
									handleExpandItem={handleExpandItem}
								/>
							)
						)}
					</tbody>
				</>
			)}
		</table>
	);
}


const TicketRowItem = ({
	editItemID,
	showEditInput,
	handleEditItem,
	handleUpdateItem,
	ticket,
	saveTickets,
	isExpanding,
	handleExpandItem,
}) => {
	const {
		id,
		subject,
		body,
		estimationpoints: estimationPoints,
		subTicketOf,
		expanded,
	} = ticket;
	const [subjectValue, setSubjectValue] = useState(subject);
	const [bodyValue, setBodyValue] = useState(body);
	const [pointsValue, setPointsValue] = useState(estimationPoints);
	const [platformValue, setPlatformValue] = useState("");

	return (
		<tr key={id}>
			<td className={strCombine(styles.tableRow_tw, "text-white w-[20%]", twConditional(subTicketOf, "pl-8"))}>
				{showEditInput && id === editItemID // check id and editItemId to only target the item clicked
					? <textarea
						className={styles.tableRowTextArea_tw}
						onChange={(e) => setSubjectValue(e.target.value)}
						value={subjectValue}
					/>
					: subTicketOf ? <div className="flex items-center"><ArrowDownRightIcon className="h-6 w-6 mr-1"/>{subjectValue}</div> : subjectValue
				}
			</td>
			<td className={strCombine(styles.tableRow_tw, "text-gray-500 w-[45%]", twConditional(subTicketOf, "pl-8"))}>
				{showEditInput && id === editItemID
					? <textarea
						className={styles.tableRowTextArea_tw}
						onChange={(e) => setBodyValue(e.target.value)}
						value={bodyValue}
					/>
					: bodyValue
				}
			</td>
			<td className={strCombine(styles.tableRow_tw, "text-gray-500 text-center w-[6%]")}>
				{showEditInput && id === editItemID
					? <input className={styles.tableRowInput_tw} onChange={(e) => setPointsValue(e.target.value)} value={pointsValue} />
					: pointsValue
				}
			</td>
			<td className={styles.tableDataSelect_tw}>
				<select id={id} className={styles.tableRowSelect_tw} onChange={(e) => setPlatformValue(e.target.value)} value={platformValue} >
					<option value="">Select an option</option>
					<option value="JIRA">Jira</option>
					<option value="SHORTCUT">Shortcut</option>
					<option value="ASANA">Asana</option>
				</select>
			</td>
			<td className={styles.tableDataButtons_tw}>
				<button
					id={`button${id}`}
					className={styles.button_tw}
					onClick={() => saveTickets(id, subject, body, estimationPoints)}
				>
					Create Ticket
				</button>
				<button
					className={strCombine("mt-2", styles.button_tw)}
					onClick={
						showEditInput
							? () => handleUpdateItem(id, subjectValue, bodyValue, pointsValue, platformValue)
							: () => handleEditItem(id)
					}
				>
					{showEditInput && id === editItemID ? "Save" : "Edit"}
				</button>
				{estimationPoints > 1  && (
					<button
						disabled={expanded}
						className={strCombine("mt-2", styles.button_tw, twConditional(expanded, styles.expandedButton_tw))}
						onClick={() => handleExpandItem(id, subject, body, estimationPoints)}
					>
						{isExpanding && id === editItemID
							? <div className={styles.expandButtonSpinner_tw}><ButtonSpinner size={"s"} />{"Expanding"}</div>
							: "Expand"
						}
					</button>
				)}
			</td>
		</tr>
	)
};