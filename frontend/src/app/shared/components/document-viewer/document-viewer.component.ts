import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DocumentDto } from '../../../core/services/document.service';

@Component({
  selector: 'app-document-viewer',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './document-viewer.component.html',
  styleUrls: ['./document-viewer.component.scss']
})
export class DocumentViewerComponent {
  @Input() doc?: DocumentDto;
  @Input() visible = false;
  @Output() closed = new EventEmitter<void>();

  copyText() {
    if (!this.doc?.data) return;
    navigator.clipboard.writeText(this.doc.data).then(() => {
      alert('Extracted text copied to clipboard');
    }, () => {
      alert('Copy failed');
    });
  }

  close() { this.closed.emit(); }
}
