export default function ButtonSpinner() {
	return (
		<svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
			<circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
			<path
				className="opacity-75"
				fill="currentColor"
				d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l1.414-1.414C2.56 15.544 1.5 13.88 1.5 12H6zm10-5.291A7.962 7.962 0 0120 12h4c0-6.627-5.373-12-12-12v4c3.042 0 5.824 1.135 7.938 3l-1.414 1.414z"
			></path>
		</svg>
	);
};
