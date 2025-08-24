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
  @Input() doc!: DocumentDto;
  @Output() deleted = new EventEmitter<string>();
  @Output() view = new EventEmitter<DocumentDto>();

  onDelete() { this.deleted.emit(this.doc.id); }
  onOpen() {
    if (this.doc.fileUrl) window.open(this.doc.fileUrl, '_blank');
  }
  onDownload() {
    // open download endpoint (if you added backend download action), otherwise open file directly
    const dl = `/api/documents/${this.doc.id}/download/`;
    // Try the download endpoint first — if it 404s the server will return an error in console.
    window.open(dl, '_blank');
  }
  onViewExtracted() {
    this.view.emit(this.doc);
  }

  mimeLabel() {
    if (!this.doc.contentType) return 'File';
    if (this.doc.contentType.includes('pdf')) return 'PDF File';
    if (this.doc.contentType.includes('image')) return 'Image File';
    return this.doc.contentType;
  }
}
