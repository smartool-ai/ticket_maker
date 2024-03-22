import { createContext, useState } from "react"

export const UploadTranscriptContext = createContext({
	ticketsResponse: {},
	setTicketsResponse: null,
	uploadResponse: {},
	setUploadResponse: null,
});

export function UploadTranscriptContextProvider({ children }) {
	const [uploadResponse, setUploadResponse] = useState(null);
	const [generationResponse, setGenerationResponse] = useState(null);
	const [ticketsResponse, setTicketsResponse] = useState(null);

	return (
		<UploadTranscriptContext.Provider value={{
			generationResponse,
			setGenerationResponse,
			ticketsResponse,
			setTicketsResponse,
			uploadResponse,
			setUploadResponse,
		}}>
			{children}
		</UploadTranscriptContext.Provider>
	)
}