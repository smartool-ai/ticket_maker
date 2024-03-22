import { createContext, useState } from "react"

export const UploadTranscriptContext = createContext({
	ticketsResponse: {},
	setTicketsResponse: null,
	uploadResponse: {},
	setUploadResponse: null,
});

export function UploadTranscriptContextProvider({ children }) {
	// const [uploadResponse, setUploadResponse] = useState(null);
	const [uploadResponse, setUploadResponse] = useState({
		"bucket": "transcriptions-ai",
		"files": {
			0: {
				"name": "Pixelum short_20240320175756.txt",
				"url": "https://transcriptions-ai.s3.us-west-2.amazonaws.com/Pixelum short.txt",
				"size": 1.917
			}
		}
	});

	// const [ticketsResponse, setTicketsResponse] = useState(null);

	const [ticketsResponse, setTicketsResponse] = useState({ tickets: [
		{
				"subject": "Evaluate Webinar Tools for Increased Reliability",
				"body": "During a recent project discussion, it was observed that some team members could not join the scheduled meeting, presumably due to technical issues with our current webinar tool. The team requires a more reliable platform to ensure every participant can join without hurdles. Evaluate and propose solutions for a webinar tool that supports our team dynamics.",
				"estimationpoints": 3
		},
		{
				"subject": "Establish Professional Email Guidelines",
				"body": "There was confusion about the appropriateness of using professional email accounts for business and work document transactions. To avoid future misunderstandings, create comprehensive guidelines on the use of professional vs. personal email accounts for all kinds of communication.",
				"estimationpoints": 2
		},
		{
				"subject": "Integrate Slack for Efficient Communication",
				"body": "Considering the suggestion to utilize Slack for speedier communication, particularly when encountering issues such as accessibility to meetings, it's proposed to fully integrate Slack into our communication strategy. This includes setting up dedicated channels for different projects and training for team members unfamiliar with Slack.",
				"estimationpoints": 4
		},
		{
				"subject": "Optimization of Team Energy Levels",
				"body": "Acknowledging the tiredness felt among team members while also feeling optimistic about the project's progress, there's a need to address work-life balance. Investigate and implement strategies or programs that boost team morale and manage energy levels effectively for sustained productivity.",
				"estimationpoints": 3
		},
		{
				"subject": "Update on Product Strategy Collaboration",
				"body": "After spending a day with a modeler discussing product strategy, significant advancements have been made. Document the updated strategy in detail, outlining the approach toward assembling necessary components for the product's development. This will serve as a roadmap for the entire team.",
				"estimationpoints": 5
		},
		{
				"subject": "Review and Plan Business Strategy",
				"body": "An update on current business strategies informed by recent discussions with business owners, emphasizing the urgency of launching the product. Create a detailed plan highlighting how to allocate resources efficiently for swift product development and prototyping.",
				"estimationpoints": 5
		},
	]});

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