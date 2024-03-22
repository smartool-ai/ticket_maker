import { createContext, useState } from "react"

export const UploadTranscriptContext = createContext({
	ticketsResponse: {},
	setTicketsResponse: null,
	uploadResponse: {},
	setUploadResponse: null,
});

export function UploadTranscriptContextProvider({ children }) {
	const [uploadResponse, setUploadResponse] = useState(null);
	const [ticketsResponse, setTicketsResponse] = useState(null);

	return (
		<UploadTranscriptContext.Provider value={{
			ticketsResponse,
			setTicketsResponse,
			uploadResponse,
			setUploadResponse,
		}}>
			{children}
		</UploadTranscriptContext.Provider>
	)
}