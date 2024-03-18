export default function HomePage({ userFirstName }) {
	return (
		<div className="text-2xl font-semibold text-white">
			{`Hello, ${userFirstName}!`}
		</div>
	)
}