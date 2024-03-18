import ButtonSpinner from '../ButtonSpinner';

export default function UploadedFilesTable({ generateTickets, response, ticketsResponse, isPolling }) {
	const generateTicketsButton = (name) => (
		<td className="py-3">
			<button
				className="relative cursor-pointer flex w-full justify-center rounded-md bg-blue-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-[#4654A3] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
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
		<table className="w-full divide-y divide-gray-300">
			<caption className="text-left text-white font-semibold pb-3">Uploaded Files</caption>
			<thead>
				<tr>
					<th scope="col" className="py-3 text-left text-sm font-semibold text-white">Size</th>
					<th scope="col" className="py-3 text-left text-sm font-semibold text-white">Name</th>
				</tr>
			</thead>
			<tbody className="divide-y divide-gray-200">
				{Object.entries(response.files).map(([index, { name, size }]) => (
					<tr key={index}>
						<td className="py-3 text-sm text-white pr-3">{size + " KB"}</td>
						<td className="py-3 text-sm text-gray-500">
							<p className="font-medium">{name}</p>
						</td>
						{generateTicketsButton(name)}
					</tr>
				))}
			</tbody>
		</table>
	);
};