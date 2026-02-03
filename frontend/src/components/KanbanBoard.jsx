import { useState } from 'react'
import { DndContext, DragOverlay, closestCorners, PointerSensor, useSensor, useSensors } from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable'
import KanbanColumn from './KanbanColumn'
import KanbanCard from './KanbanCard'

const KanbanBoard = ({ applications, onEdit, onDelete, onStatusUpdate, onFavoriteToggle }) => {
  const [activeId, setActiveId] = useState(null)

  const statuses = ['Applied', 'Phone Screen', 'Interview', 'Offer', 'Rejected']

  // Group applications by status
  const columns = statuses.reduce((acc, status) => {
    acc[status] = applications.filter(app => app.status === status)
    return acc
  }, {})

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  )

  const handleDragStart = (event) => {
    setActiveId(event.active.id)
  }

  const handleDragEnd = (event) => {
    const { active, over } = event

    if (!over) {
      setActiveId(null)
      return
    }

    const activeApp = applications.find(app => app.id === active.id)
    const overStatus = over.id

    // If dropped on a column (status), update the application status
    if (statuses.includes(overStatus) && activeApp && activeApp.status !== overStatus) {
      onStatusUpdate(activeApp.id, overStatus)
    }

    setActiveId(null)
  }

  const handleDragCancel = () => {
    setActiveId(null)
  }

  const activeApplication = applications.find(app => app.id === activeId)

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCorners}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onDragCancel={handleDragCancel}
    >
      <div className="flex gap-4 overflow-x-auto pb-4 animate-fade-in">
        {statuses.map((status) => (
          <SortableContext
            key={status}
            id={status}
            items={columns[status].map(app => app.id)}
            strategy={verticalListSortingStrategy}
          >
            <KanbanColumn
              status={status}
              applications={columns[status]}
              onEdit={onEdit}
              onDelete={onDelete}
              onFavoriteToggle={onFavoriteToggle}
              formatDate={formatDate}
            />
          </SortableContext>
        ))}
      </div>

      <DragOverlay>
        {activeApplication ? (
          <div className="opacity-50">
            <KanbanCard
              application={activeApplication}
              formatDate={formatDate}
              isDragging={true}
            />
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  )
}

export default KanbanBoard
