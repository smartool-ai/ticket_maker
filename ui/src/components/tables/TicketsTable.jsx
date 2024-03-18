import ButtonSpinner from '../ButtonSpinner';

export default function TicketTable({ saveTickets, ticketsResponse, isPolling }) {
	const ticketRowItem = (key, subject, body, estimationPoints) => (
		<tr key={key}>
			<td className="py-3 text-sm text-white pr-3 w-[25%]">{subject}</td>
			<td className="py-3 text-sm text-gray-500 pr-3 w-[55%]">{body}</td>
			<td className="py-3 text-sm text-gray-500 pr-3 text-center">{estimationPoints}</td>
			<td className="w-[10%]">
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
					className="cursor-pointer rounded-md bg-blue-600 py-1 px-3 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-[#4654A3] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
					onClick={() => saveTickets(key, subject, body, estimationPoints)}
				>
					Upload Ticket
				</button>
			</td>
		</tr>
	);

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
						</tr>
					</thead>
					<tbody className="divide-y divide-gray-200">
						{ticketsResponse && ticketsResponse.tickets && Object.entries(ticketsResponse.tickets).map(
							([key, { subject, body, estimationpoints }]) => ticketRowItem(key, subject, body, estimationpoints)
						)}
					</tbody>
				</>
			)}
		</table>
	);
};