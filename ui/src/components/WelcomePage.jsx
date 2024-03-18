import Logo from './Logo';

export default function WelcomePage({ loginWithPopup }) {
	return (
		<div className="h-full w-full flex flex-col items-center justify-center gap-y-6">
			<Logo />
			<button
				onClick={() => loginWithPopup()}
				className="rounded-md bg-blue-600 px-5 py-2.5 text-lg font-semibold text-white hover:bg-[#4654A3] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
			>
				Sign in
			</button>
		</div>
	);
};