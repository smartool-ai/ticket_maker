import { Fragment } from 'react';
import { Transition } from '@headlessui/react';
import {
	CheckCircleIcon,
	InformationCircleIcon,
	ExclamationTriangleIcon,
	ExclamationCircleIcon,
	XMarkIcon
} from '@heroicons/react/20/solid';


export default function Toast({ label, onClose, type = "info" }) {
	const alertType = {
		error: <ExclamationCircleIcon />,
		info: <InformationCircleIcon />,
		success: <CheckCircleIcon />,
		warning: <ExclamationTriangleIcon />,
	};

	const bgColor = {
		error: "bg-red-600",
		info: "bg-blue-400",
		success: "bg-green-600",
		warning: "bg-orange-400",
	};

	return (
		<div className="relative">
			<Transition
				appear
				as={Fragment}
				enter="transform ease-out duration-300 transition"
				enterFrom="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
				enterTo="translate-y-0 opacity-100 sm:translate-x-0"
				show
			>
				<div className={["rounded-md p-4 flex gap-2 max-w-fit absolute z-10 right-0", bgColor[type]].join(" ")}>
					<div className="h-5 w-5 text-white" aria-hidden="true">
						{alertType[type]}
					</div>
					<p className="text-sm text-white font-semibold">
						{label}
					</p>
					<div className="h-5 w-5 text-white font-bold hover:border-2 hover:rounded-md ml-1" onClick={onClose}>
						<XMarkIcon />
					</div>
				</div>
			</Transition>
		</div>
	)
}