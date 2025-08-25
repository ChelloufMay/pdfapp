// frontend/src/app/shared/components/file-card/file-card.component.ts
// File card component: displays basic info about a document and exposes actions:
// - visible actions: View, Delete
// - 3-dot menu actions: Open in new tab, Download
//
// Important: when Delete is clicked we now close the menu first, then emit the delete event,
// so the UI doesn't leave the menu open while the confirm dialog appears.

import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DocumentDto } from '../../../core/services/document.service';

@Component({
  selector: 'app-file-card',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './file-card.component.html',
  styleUrls: ['./file-card.component.scss']
})
export class FileCardComponent {
  // Document data passed from parent
  @Input() doc!: DocumentDto;

  // Emitted when user requests deletion (emits the document id)
  @Output() deleted = new EventEmitter<string>();

  // Emitted when user wants to view the extracted content (emits the whole document object)
  @Output() view = new EventEmitter<DocumentDto>();

  // internal UI state for whether the 3-dot menu is visible
  showMenu = false;

  // toggle the 3-dot menu visibility
  toggleMenu() {
    this.showMenu = !this.showMenu;
  }

  // Called when the visible "Delete" button is clicked.
  // We close the menu immediately (good UX) and then emit the delete request.
  onDelete() {
    // close the popup if open so the UI is tidy while confirmation is shown
    this.showMenu = false;
    // emit id so parent (Home) can show confirmation and perform deletion
    this.deleted.emit(this.doc.id);
  }

  // Called when the visible "View" button is clicked
  // Emit the document so the parent can open the viewer modal
  onView() {
    this.view.emit(this.doc);
  }

  // Open the original file in a new tab (browser will display or download depending on headers)
  onOpen() {
    if (this.doc?.fileUrl) {
      window.open(this.doc.fileUrl, '_blank', 'noopener');
    }
  }

  // Try a download endpoint if one exists on the backend, otherwise open the fileUrl.
  // If you implemented /api/documents/<id>/download/ on the backend, that endpoint will force
  // a file download via Content-Disposition headers.
  onDownload() {
    const dl = `/api/documents/${this.doc.id}/download/`;
    // open the download endpoint in a new tab/window
    window.open(dl, '_blank', 'noopener');
  }

  // Small helper to display a human friendly label for the MIME type
  mimeLabel(): string {
    if (!this.doc?.contentType) return 'File';
    const m = this.doc.contentType.toLowerCase();
    if (m.includes('pdf')) return 'PDF';
    if (m.includes('image')) return 'Image';
    if (m.includes('word') || m.includes('msword') || m.includes('officedocument')) return 'Document';
    return this.doc.contentType;
  }
}
