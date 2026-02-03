import { useDroppable } from '@dnd-kit/core'
import KanbanCard from './KanbanCard'

const KanbanColumn = ({ status, applications, onEdit, onDelete, onFavoriteToggle, formatDate }) => {
  const { setNodeRef, isOver } = useDroppable({
    id: status,
  })

  // Status color mapping
  const getStatusColor = (status) => {
    const colors = {
      'Applied': 'from-gray-500 to-gray-600',
      'Phone Screen': 'from-teal-500 to-teal-600',
      'Interview': 'from-amber-500 to-amber-600',
      'Offer': 'from-green-500 to-green-600',
      'Rejected': 'from-red-500 to-red-600'
    }
    return colors[status] || 'from-gray-500 to-gray-600'
  }

  return (
    <div
      className={`flex-shrink-0 w-80 bg-gray-50 dark:bg-gray-800 rounded-xl border-2 transition-all duration-200 ${
        isOver
          ? 'border-green-500 dark:border-green-400 shadow-xl'
          : 'border-gray-200 dark:border-gray-700'
      }`}
    >
      {/* Column Header */}
      <div className={`bg-gradient-to-r ${getStatusColor(status)} px-4 py-3 rounded-t-xl`}>
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-white text-sm">{status}</h3>
          <span className="bg-white bg-opacity-30 text-white text-xs font-bold px-2 py-1 rounded-full">
            {applications.length}
          </span>
        </div>
      </div>

      {/* Cards Container */}
      <div
        ref={setNodeRef}
        className="p-3 space-y-3 min-h-[500px] max-h-[calc(100vh-300px)] overflow-y-auto"
      >
        {applications.length === 0 ? (
          <div className="text-center py-8">
            <svg className="mx-auto h-8 w-8 text-gray-400 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
            </svg>
            <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">No applications</p>
          </div>
        ) : (
          applications.map((app) => (
            <KanbanCard
              key={app.id}
              application={app}
              onEdit={onEdit}
              onDelete={onDelete}
              onFavoriteToggle={onFavoriteToggle}
              formatDate={formatDate}
            />
          ))
        )}
      </div>
    </div>
  )
}

export default KanbanColumn
