import { Fragment } from 'react';
import { Transition } from '@headlessui/react';
import {
    CheckCircleIcon,
    InformationCircleIcon,
    ExclamationTriangleIcon,
    ExclamationCircleIcon,
    XCircleIcon
} from '@heroicons/react/20/solid';


export default function Toast({ label, onClose, type = "info" }) {
    const alertType = {
        error: <ExclamationCircleIcon className="text-red-600"/>,
        info: <InformationCircleIcon className="text-blue-400"/>,
        success: <CheckCircleIcon className="text-green-600"/>,
        warning: <ExclamationTriangleIcon className="text-orange-400"/>,
    };

    return (
        <div className="relative">
            <Transition
                appear
                as={Fragment}
                enter="transform ease-out duration-300 transition"
                enterFrom="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
                enterTo="translate-y-0 opacity-100 sm:translate-x-0"
                leave="transition-opacity duration-75"
                leaveFrom="opacity-100"
                leaveTo="opacity-0"
                show
                >
                <div className="bg-gray-100 rounded-md p-4 flex gap-2 max-w-fit absolute z-10 right-0">
                    <div className="h-5 w-5" aria-hidden="true">
                        {alertType[type]}
                    </div>
                    <div className="text-sm text-gray-700">
                        {label}
                    </div>
                    <div className="h-5 w-5 text-gray-700 hover:text-[#4654A3] ml-1" onClick={onClose}>
                        <XCircleIcon />
                    </div>
                </div>
            </Transition>
        </div>
    )
}