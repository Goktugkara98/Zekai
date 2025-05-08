/**
 * ZekAI Drag and Drop Module
 * =======================
 * @description Panel drag and drop functionality using SortableJS library
 * @version 1.0.0
 * @author ZekAI Team
 * @requires SortableJS
 * 
 * TABLE OF CONTENTS
 * ================
 * 1. Drag and Drop Operations
 *    1.1 Panel Dragging
 */

//=============================================================================
// 1. DRAG AND DROP OPERATIONS
//=============================================================================

/**
 * 1.1 Panel Dragging
 * ---------------
 */

/**
 * Enables drag and drop functionality for AI panels
 * Only activates when multiple panels are present
 * Uses SortableJS to handle the drag operations
 * 
 * @returns {Sortable|null} The Sortable instance or null if not enabled
 */
function enablePanelDrag() {
    // Only enable dragging when multiple panels exist
    if (state.panelCount <= 1) {
        console.log('Drag and drop not enabled: Need multiple panels');
        return null;
    }
    
    // Verify panel area exists
    if (!elements.panelArea) {
        console.warn('Panel area element not found in DOM');
        return null;
    }
    
    try {
        // Initialize SortableJS on the panel area
        const sortable = Sortable.create(elements.panelArea, {
            // Animation duration in ms
            animation: 180,
            
            // Delay before drag starts
            delay: 150,
            delayOnTouchOnly: true,
            
            // Which elements can be dragged
            draggable: '.ai-panel',
            
            // Class added to ghost element during drag
            ghostClass: 'dragging',
            
            /**
             * Callback when dragging starts
             * @param {SortableEvent} evt - The SortableJS event object
             */
            onStart: function(evt) {
                document.body.classList.add('dragging-active');
                console.log('Panel drag started:', evt.item.id || 'unnamed panel');
            },
            
            /**
             * Callback when dragging ends
             * @param {SortableEvent} evt - The SortableJS event object
             */
            onEnd: function(evt) {
                document.body.classList.remove('dragging-active');
                console.log('Panel drag ended. New index:', evt.newIndex);
            }
        });
        
        console.log('Panel drag and drop enabled successfully');
        return sortable;
    } catch (error) {
        console.error('Failed to initialize drag and drop:', error);
        return null;
    }
}
