import { InformationCircleIcon } from '@heroicons/react/20/solid'

export default function Notice({ children }) {
  return <div className="flex flex-col gap-6">
    <div className="rounded-md bg-gray-100 p-4">
      <div className="flex gap-3">
        <div className="flex-shrink-0">
          <InformationCircleIcon className="h-5 w-5 text-blue-400" aria-hidden="true" />
        </div>
        <div className="text-sm text-blue-700 flex flex-col gap-2">
          {children}
        </div>
      </div>
    </div>
  </div>
}
