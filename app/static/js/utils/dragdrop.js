/**
 * Drag and drop functionality using SortableJS
 */

/**
 * Enable drag and drop functionality for panels
 */
function enablePanelDrag() {
    if (state.panelCount > 1) {
        const sortable = Sortable.create(elements.panelArea, {
            animation: 180,
            delay: 150,
            delayOnTouchOnly: true,
            draggable: '.ai-panel',
            ghostClass: 'dragging',
            onStart: function(evt) {
                document.body.classList.add('dragging-active');
            },
            onEnd: function(evt) {
                document.body.classList.remove('dragging-active');
            }
        });
    }
}
